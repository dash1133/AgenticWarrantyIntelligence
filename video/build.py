"""Assemble awi-video.html from the player template and the two source pages.

The source pages stay the source of truth for beats 4 to 9: edit them, then rerun
    python3 build.py
"""
import base64
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
template = (HERE / "player.template.html").read_text(encoding="utf-8")
frames_src = (HERE / "source/warrantyai-video-frames.html").read_text(encoding="utf-8")
overview_src = (HERE / "source/agentic-warranty-intelligence.html").read_text(encoding="utf-8")

frames = re.findall(r'<section class="frame".*?</section>', frames_src, flags=re.S)
if len(frames) != 5:
    raise SystemExit(f"expected 5 frames (beats 5 to 9), found {len(frames)}")

overview = re.search(r'<div id="stage">\s*(.*?)\s*</div>\s*</div>\s*<div id="hud">', overview_src, flags=re.S)
if not overview:
    raise SystemExit("could not find the overview stage markup")

alignment = HERE / "vo/alignment.json"
vo = alignment.read_text(encoding="utf-8") if alignment.exists() else "null"

font = base64.b64encode((HERE / "fonts/ibm-plex-sans-latin.woff2").read_bytes()).decode("ascii")

out = (template
       .replace("<!--OVERVIEW-->", overview.group(1))
       .replace("<!--FRAMES-->", "\n".join(frames))
       .replace("/*FONT*/", "data:font/woff2;base64," + font)
       .replace("/*VO*/null", vo))
(HERE / "awi-video.html").write_text(out, encoding="utf-8")
print("wrote awi-video.html")
