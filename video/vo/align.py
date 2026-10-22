"""Line up each scripted line (cue) with the recorded voiceover.

No speech recognition is available here, so this uses the pauses in the read:
the speech between pauses is grouped, in order, into one group per cue, choosing
the grouping whose lengths best match each line's expected length (by character
count) and that breaks at the longest pauses.
    python3 vo/align.py      -> vo/alignment.json (speech start and end of each cue)
"""
import json
import math
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "voiceover.mp3"
cues = json.loads((HERE / "cues.json").read_text())

out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(SRC), "-af", "silencedetect=noise=-38dB:d=0.12",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
total = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).group(3)) + 60 * int(re.search(r"Duration: (\d+):(\d+)", out).group(2))
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
sil = list(zip(starts, ends + [total] * (len(starts) - len(ends))))

# Speech runs between silences.
runs, t = [], 0.0
for s, e in sil:
    if s - t > 0.05:
        runs.append((t, s))
    t = e
if total - t > 0.05:
    runs.append((t, total))
gap_after = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)] + [0]

chars = [len(re.sub(r"[^A-Za-z0-9]", "", c["text"])) + 6 for c in cues]
speech_total = runs[-1][1] - runs[0][0]
scale = speech_total / sum(chars)
exp = [c * scale for c in chars]

M, C = len(runs), len(cues)
INF = float("inf")
best = [[INF] * (M + 1) for _ in range(C + 1)]
back = [[0] * (M + 1) for _ in range(C + 1)]
best[0][0] = 0.0
for c in range(1, C + 1):
    for j in range(c, M + 1):
        for i in range(c - 1, j):
            if best[c - 1][i] == INF:
                continue
            dur = runs[j - 1][1] - runs[i][0]
            cost = ((dur - exp[c - 1]) / max(exp[c - 1], 1.0)) ** 2 * 4
            if j < M:
                cost -= 0.6 * math.log(max(gap_after[j - 1], 0.05) / 0.05)
            v = best[c - 1][i] + cost
            if v < best[c][j]:
                best[c][j], back[c][j] = v, i
bounds, j = [], M
for c in range(C, 0, -1):
    i = back[c][j]
    bounds.append((i, j))
    j = i
bounds.reverse()

result = []
for k, (i, j) in enumerate(bounds):
    s, e = runs[i][0], runs[j - 1][1]
    result.append({"cue": k, "beat": cues[k]["beat"], "text": cues[k]["text"], "start": round(s, 3), "end": round(e, 3),
                   "ratio": round((e - s) / exp[k], 2), "pause_after": round(gap_after[j - 1], 2)})
(HERE / "alignment.json").write_text(json.dumps({"source": SRC.name, "duration": total, "cues": result}, indent=1))
for r in result:
    print(f"{r['start']:7.2f}-{r['end']:7.2f}  x{r['ratio']:.2f}  gap {r['pause_after']:.2f}  {r['text'][:70]}")
