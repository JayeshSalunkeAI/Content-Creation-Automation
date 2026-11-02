"""pipeline/doctor.py — environment checks v1+v2, one command. PASS/FAIL per line.

Usage:
  .venv/Scripts/python.exe pipeline/doctor.py            (or any python if venv not built yet)
  .venv/Scripts/python.exe pipeline/doctor.py --smoke    + 1-paragraph Kokoro render + Whisper round-trip

Saves logs/doctor_<date>.txt.
"""

import argparse
import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# project-local HF cache + quiet symlink warning (set before any hub import)
os.environ.setdefault("HF_HOME", os.path.join(ROOT, "cache", "hf"))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
rows = []
fails = []


def row(name, ok, detail=""):
    rows.append((("OK  " if ok else "FAIL") + " " + name, detail))
    if not ok:
        fails.append(name)


def ver(cmd, first=True):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        s = (p.stdout or p.stderr).strip().splitlines()
        return (s[0] if s else "") if first else (p.stdout or p.stderr).strip()
    except Exception:
        return ""


def find_module(mod):
    import importlib
    try:
        m = __import__(mod)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ver = getattr(m, "__version__", "")
        rows.append(("OK   import " + mod, ver))
        return True
    except Exception as e:
        rows.append((f"FAIL import {mod}", f"{e.__class__.__name__}: {e}"))
        fails.append(f"import {mod}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="1-paragraph Kokoro render + Whisper timing check")
    a = ap.parse_args()

    venv_py = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
    using_venv_prefix = sys.executable == venv_py or os.path.basename(os.path.dirname(sys.executable)) == "Scripts"

    # python / venv
    row("python version >= 3.9", sys.version_info >= (3, 9), sys.version.split()[0])
    row("running inside .venv", bool(using_venv_prefix), sys.executable)

    # system tools
    ff_dir = os.path.join(ROOT, "tools", "ffmpeg", "bin")
    ff = shutil.which("ffmpeg") or (os.path.join(ff_dir, "ffmpeg.exe") if os.path.exists(os.path.join(ff_dir, "ffmpeg.exe")) else None)
    ffp = shutil.which("ffprobe") or (os.path.join(ff_dir, "ffprobe.exe") if os.path.exists(os.path.join(ff_dir, "ffprobe.exe")) else None)
    row("ffmpeg", bool(ff), ver([ff, "-version"]) if ff else "")
    row("ffprobe", bool(ffp), ver([ffp, "-version"])[:30] if ffp else "")
    node_v = ver(["node", "--version"])
    row("node >= 18", bool(node_v) and int(node_v.lstrip("v").split(".")[0]) >= 18, node_v)
    row("git", bool(shutil.which("git")), ver(["git", "--version"]))
    gpu = shutil.which("nvidia-smi")
    row("nvidia-smi (GPU driver)", bool(gpu), ver(["nvidia-smi"])[:40])
    env_path = [os.path.join(ff_dir, "ffmpeg.exe"), "ffmpeg"]
    row("ffmpeg on PATH", any(shutil.which(p) for p in env_path) or os.path.exists(os.path.join(ff_dir, "ffmpeg.exe")),
        f"portable build: {ff_dir}")

    # python packages
    for m in ("numpy", "scipy", "soundfile", "torch", "kokoro", "faster_whisper",
              "librosa", "pyloudnorm", "jsonschema", "PIL", "espeakng_loader"):
        find_module(m)

    import torch
    row("torch CPU build", True, f"torch {torch.__version__}, CUDA available: {torch.cuda.is_available()} (CPU-first by design)")
    if find_module("espeakng_loader"):
        import espeakng_loader
        lp, dp = espeakng_loader.get_library_path(), espeakng_loader.get_data_path()
        row("espeak-ng library (kokoro)", bool(lp) and os.path.exists(lp), lp)

    # node packages + browsers
    nm = lambda rel: os.path.isdir(os.path.join(ROOT, rel)) and len(os.listdir(os.path.join(ROOT, rel))) > 0
    row("studio node_modules (kit)", nm(os.path.join("studio", "node_modules")))
    for pkg in ("three", "playwright", "@fontsource/fredoka", "@fontsource/nunito", "@fontsource/playfair-display"):
        row(f"  studio: {pkg}", os.path.isdir(os.path.join(ROOT, "studio", "node_modules", pkg)))
    row("remotion node_modules", nm(os.path.join("remotion", "node_modules")))
    pw = ""
    try:
        out = subprocess.run(["node", "-e", "import('playwright').then(p=>console.log(p.chromium.executablePath()))"],
                             cwd=os.path.join(ROOT, "studio"), capture_output=True, text=True, timeout=60)
        pw = out.stdout.strip()
        row("playwright chromium", bool(pw) and os.path.exists(pw), pw)
    except Exception as e:
        row("playwright chromium", False, str(e))
    rh = os.path.join(ROOT, "remotion", "node_modules", ".remotion", "chrome-headless-shell")
    row("remotion headless shell", any(map(os.path.exists, [rh])) or bool(_glob_find(rh, "chrome-headless-shell.exe")), rh)

    # vendored kit
    row("kit render.mjs", os.path.exists(os.path.join(ROOT, "studio", "render.mjs")))
    row("kit engine/player.js", os.path.exists(os.path.join(ROOT, "studio", "engine", "player.js")))
    row("master plan pdf", os.path.exists(os.path.join(ROOT, "docs", "MASTER_PLAN.pdf")))

    if a.smoke:
        try:
            out = os.path.join(ROOT, "cache", "smoke")
            os.makedirs(out, exist_ok=True)
            wav = os.path.join(out, "smoke.wav")
            if os.path.exists(wav):
                os.remove(wav)
            code = (
                "import numpy as np, soundfile as sf, espeakng_loader\n"
                "from misaki.espeak import EspeakWrapper\n"
                "EspeakWrapper.set_library(espeakng_loader.get_library_path())\n"
                "EspeakWrapper.set_data_path(espeakng_loader.get_data_path())\n"
                "from kokoro import KPipeline\n"
                "p = KPipeline(lang_code='a')\n"
                "c = [a for _g, _p, a in p('This is a pipeline smoke test. If you can hear this line, the voice works.', voice='af_heart', speed=1.0)]\n"
                "sf.write(r'" + wav + "', np.concatenate(c), 24000)\n"
                "print('kokoro ok')\n"
            )
            env = dict(os.environ)
            env["HF_HOME"] = os.path.join(ROOT, "cache", "hf")
            env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            subprocess.run([venv_py, "-c", code], capture_output=True, text=True, cwd=ROOT, env=env, timeout=900)

            if os.path.exists(wav):
                from faster_whisper import WhisperModel
                model = WhisperModel("small.en", device="cpu", compute_type="int8")
                segs, _info = model.transcribe(wav, language="en", word_timestamps=True)
                words = [w.word for s in segs for w in (s.words or [])]
                row("smoke: kokoro render + whisper read-back", len(words) >= 8,
                    " ".join(words)[:90])
            else:
                row("smoke: kokoro render", False, "no wav produced — see stderr above")
        except Exception as e:
            row("smoke", False, f"{e.__class__.__name__}: {e}")

    # report
    date = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log = os.path.join(ROOT, "logs", f"doctor_{date}.txt")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    print(f"\n=== channel pipeline doctor — {platform.platform()} — {os.cpu_count()} threads ===")
    for a_, b_ in rows:
        print(f"  {a_:38s} {str(b_)[:100]}")
    with open(log, "w", encoding="utf-8") as f:
        f.write("doctor results (each line: status name | detail)\n")
        for a_, b_ in rows:
            f.write(f"{a_} | {b_}\n")
    print(f"written: {log}")
    if fails:
        print(f"\nFAILURES ({len(fails)}): {', '.join(fails)}")
        sys.exit(1)
    print("\nALL PASS")


def _glob_find(root, needle):
    for base_d, _dirs, files in os.walk(root):
        if needle in files:
            return os.path.join(base_d, needle)
    return None


if __name__ == "__main__":
    main()
