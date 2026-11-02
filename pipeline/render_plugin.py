"""pipeline/render_plugin.py — invoke the vendored kit renderer (stages P7/QC-1/P8).

Usage:
  .venv/Scripts/python.exe pipeline/render_plugin.py --video <id>                    # full silent video (Mode A)
  ... --video <id> --sheet                                                          # contact sheets (QC-1)
  ... --video <id> --stills 3.5,12                                                  # stills at times
  ... --video <id> --from 0 --to 12 --out FILE [--scale 0.5]                        # range render (Mode B / preview)

Reads config/pipeline.json (workers, gl, format, crf). Automates exactly the verified
render.mjs options; result names: full -> studio/projects/<id>/build/video_silent.mp4,
range (no --out) -> build/preview.mp4, --sheet -> build/sheets/sheet_NN.png.
"""

import argparse
import os

from _common import (ROOT, STUDIO, ensure_env, load_config, run, studio_project,
                     load_json, video_dir)

RENDER_MJS = os.path.join(STUDIO, "render.mjs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--stills", help="comma times, e.g. 3.5,12")
    ap.add_argument("--styles", help="style grid, e.g. dusk,midnight,brand")
    ap.add_argument("--at", help="times for --styles grid")
    ap.add_argument("--from", dest="s_from", type=float)
    ap.add_argument("--to", dest="s_to", type=float)
    ap.add_argument("--out")
    ap.add_argument("--scale", type=float)
    ap.add_argument("--workers", type=int)
    ap.add_argument("--gl")
    ap.add_argument("--format", dest="fmt", choices=["png", "jpeg"])
    ap.add_argument("--crf", type=int)
    ap.add_argument("--preset")
    ap.add_argument("--debug", action="store_true")
    a = ap.parse_args()

    cfg = load_config()["plugin"]
    cmd = ["node", os.path.abspath(RENDER_MJS), "--project", os.path.abspath(studio_project(a.video))]

    def style_id():
        master = os.path.join(video_dir(a.video), "master.json")
        # style comes from the generated config.json (make_plugin_files decides brand vs fallback)
        pcfg = load_json(os.path.join(studio_project(a.video), "config.json"))
        return pcfg.get("style") or cfg.get("style_fallback", "dusk")

    if a.sheet:
        cmd.append("--sheet")
    elif a.stills:
        cmd += ["--stills", a.stills]
    elif a.styles:
        cmd += ["--styles", a.styles, "--at", a.at or "1"]
    elif a.s_from is not None or a.s_to is not None:
        if a.s_from is not None:
            cmd += ["--from", str(a.s_from)]
        if a.s_to is not None:
            cmd += ["--to", str(a.s_to)]
        if a.out:
            cmd += ["--out", os.path.abspath(a.out)]
    if a.scale is not None:
        cmd += ["--scale", str(a.scale)]
    if a.workers:
        cmd += ["--workers", str(a.workers)]
    else:
        cmd += ["--workers", str(cfg["workers"])]
    cmd += ["--gl", a.gl or cfg["gl"], "--format", a.fmt or cfg["format"],
            "--crf", str(a.crf or cfg["crf"])]
    if a.preset:
        cmd += ["--preset", a.preset]
    if a.debug:
        cmd.append("--debug")
    # render.mjs: --style URL-override; harmless + pins intent if config changed since gen
    cmd += ["--style", style_id()]

    print(" ".join(cmd))
    p = run(cmd, cwd=ROOT, check=False)
    print((p.stdout or "")[-4000:])
    if p.returncode != 0:
        print((p.stderr or "")[-1500:])
        raise SystemExit(p.returncode)

    # existence check of expected artifacts
    build = os.path.join(studio_project(a.video), "build")
    if a.sheet:
        sheets = os.path.join(build, "sheets")
        if not os.path.isdir(sheets) or not any(os.scandir(sheets)):
            raise SystemExit("no contact sheets written to build/sheets — check log above")
        print(f"sheets ok: {sheets}")
    elif a.s_from is not None and a.s_to is not None:
        target = a.out or os.path.join(build, "preview.mp4")
        if not os.path.exists(target):
            raise SystemExit(f"range render did not produce {target}")
        print(f"range ok: {target}")
    elif not (a.stills or a.styles):
        target = os.path.join(build, "video_silent.mp4")
        if not os.path.exists(target):
            raise SystemExit(f"full render did not produce {target}")
        print(f"full render ok: {target}")


if __name__ == "__main__":
    main()
