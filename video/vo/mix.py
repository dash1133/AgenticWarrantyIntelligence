"""Cut the voiceover to the video's schedule and mix it with the score.

    node render.cjs --stills   (writes vo/schedule.json and music/timeline.json)
    python3 music/score.py
    python3 vo/mix.py          -> vo/voice.wav, out/final-mix.wav

Each cue's slice of the recording (its line plus the natural pause after it) is placed
at the cue's start in the video. The slices meet inside pauses, so the cuts are silent.
The music sits about 11 dB under the voice and dips a few dB more while the voice speaks.
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SR = 44100
sched = json.loads((HERE / "schedule.json").read_text())

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(HERE / "voiceover.mp3"), "-f", "f32le", "-ac", "1",
                      "-ar", str(SR), "-"], capture_output=True, check=True).stdout
src = np.frombuffer(raw, dtype="<f4").astype(np.float64)

out = np.zeros(int((sched["duration"] + 1.0) * SR))
fade = int(0.008 * SR)
for c in sched["cues"]:
    a, b = c["src"]
    seg = src[int(a * SR):int(b * SR)].copy()
    ramp = np.linspace(0, 1, fade)
    seg[:fade] *= ramp
    seg[-fade:] *= ramp[::-1]
    i = int(c["start"] * SR)
    out[i:i + len(seg)] += seg[: len(out) - i]

pcm = (np.clip(out, -1, 1) * 32767).astype("<i2")
with wave.open(str(HERE / "voice.wav"), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

(ROOT / "out").mkdir(exist_ok=True)
graph = ("[0:a]loudnorm=I=-16:TP=-2:LRA=11,aformat=channel_layouts=stereo,asplit=2[v][sc];"
         "[1:a]loudnorm=I=-16:TP=-2:LRA=11,volume=-11dB[m];"
         "[m][sc]sidechaincompress=threshold=0.04:ratio=3:attack=40:release=600[md];"
         "[v][md]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89:level=false[a]")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(HERE / "voice.wav"), "-i", str(ROOT / "music/score.wav"),
                "-filter_complex", graph, "-map", "[a]", "-ar", str(SR), str(ROOT / "out/final-mix.wav")], check=True)
print("wrote vo/voice.wav and out/final-mix.wav")
