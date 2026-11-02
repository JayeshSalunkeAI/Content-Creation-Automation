"""pipeline/_common.py — shared helpers for every stage script.

Conventions:
- ROOT is C:\\channel (parent of this pipeline/ folder).
- Python: always C:\\channel\\.venv\\Scripts\\python.exe (never bare python/py -3).
- ffmpeg: portable build at C:\\channel\\tools\\ffmpeg\\bin (fall back to PATH).
"""

import json
import os
import subprocess
import sys

# Project-local HF cache for every pipeline process (set before any hub import happens).
os.environ.setdefault("HF_HOME", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "hf"))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
FFMPEG_DIR = os.path.join(ROOT, "tools", "ffmpeg", "bin")

STUDIO = os.path.join(ROOT, "studio")
REMOTION = os.path.join(ROOT, "remotion")
VIDEOS = os.path.join(ROOT, "videos")
LIBRARY = os.path.join(ROOT, "library")
CACHE = os.path.join(ROOT, "cache")


def load_json(path, default=None):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def load_config():
    return load_json(os.path.join(ROOT, "config", "pipeline.json"))


def video_dir(vid):
    return os.path.join(VIDEOS, vid)


def studio_projects_dir():
    return os.path.join(STUDIO, "projects")


def studio_project(vid):
    return os.path.join(STUDIO, "projects", vid)


def ensure_env(env=None):
    """Env guaranteeing ffmpeg/ffprobe on PATH and UTF-8 python defaults."""
    e = dict(env or os.environ)
    if FFMPEG_DIR and os.path.isdir(FFMPEG_DIR) and FFMPEG_DIR not in e.get("PATH", ""):
        e["PATH"] = FFMPEG_DIR + os.pathsep + e.get("PATH", "")
    e["PYTHONUTF8"] = "1"
    e.setdefault("HF_HOME", os.path.join(CACHE, "hf"))
    return e


def run(cmd, env=None, cwd=None, check=True, capture=True):
    p = subprocess.run(cmd, env=ensure_env(env), cwd=cwd,
                       capture_output=capture, text=True)
    if check and p.returncode != 0:
        tail = (p.stderr or "")[-2000:]
        sys.exit(f"command failed ({' '.join(cmd[:2])} …): {tail}")
    return p


def ffmpeg_exe(name="ffmpeg.exe"):
    for d in (FFMPEG_DIR,):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return name  # rely on PATH


def probe_duration(path):
    out = run([ffmpeg_exe("ffprobe.exe"), "-v", "error", "-show_entries",
               "format=duration", "-of", "default=nw=1:nk=1", path]).stdout
    return float(out.strip())


def fail(msg, code=1):
    print(f"FAIL: {msg}")
    sys.exit(code)


def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
