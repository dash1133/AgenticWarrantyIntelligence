"""Original temp score for the Agentic Warranty Intelligence video.

Synthesised from scratch (no samples), so it carries no licence. Sections follow the
beat start times in timeline.json, which render.cjs writes; rerun after any retiming:
    python3 score.py            -> score.wav (stereo, 44.1 kHz)

Arc: B minor tension under the problem, a lift into D major on the reveal, a steady
pulse that builds through the walkthrough, a drop under "Your people make the call",
and a full, resolved close.
"""
import json
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR = 44100
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT

timeline = json.loads((HERE / "timeline.json").read_text())
DUR = timeline["duration"] + 1.0
starts = {k.split(" ·")[0]: v for k, v in timeline["beats"].items()}
N = int(DUR * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def bar_at(t):
    """Section changes land on the nearest bar line, so the music stays on grid."""
    return round(t / BAR) * BAR


S = {k: bar_at(v) for k, v in starts.items()}
S["End"] = DUR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def env(n, a, r, total):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) if a > 0 else np.ones(n)
    tail = np.clip((total - t) / r, 0, 1)
    return e * tail


# Chords as MIDI notes (pad voicing around middle C) with a bass root.
CH = {
    "Bm": ([59, 62, 66, 71], 35), "G": ([55, 59, 62, 67], 31), "Em": ([55, 59, 64, 67], 28),
    "F#": ([54, 58, 61, 66], 30), "D": ([57, 62, 66, 69], 38), "A": ([57, 61, 64, 69], 33),
    "Asus": ([57, 62, 64, 69], 33),
}


def pad(name, t0, length, cutoff, gain):
    notes, _ = CH[name]
    total = length + 1.6
    n = int(total * SR)
    t = np.arange(n) / SR
    e = env(n, 0.9, 1.6, total)
    for note in notes:
        f0 = midi(note)
        for det, pan in ((-0.07, -0.6), (0.0, 0.0), (0.07, 0.6)):
            f = f0 * 2 ** (det / 12)
            k_max = max(1, int(cutoff / f))
            sig = np.zeros(n)
            for k in range(1, min(k_max, 24) + 1):
                sig += np.sin(2 * np.pi * k * f * t + k * 0.7) / k ** 1.4
            add(sig * e, t0, pan, gain * 0.05)


def pluck(note, t0, decay, gain, pan, bright=0.35):
    n = int((decay * 6) * SR)
    t = np.arange(n) / SR
    f = midi(note)
    sig = np.sin(2 * np.pi * f * t) + bright * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    sig *= np.exp(-t / decay) * np.minimum(1, t / 0.004)
    add(sig, t0, pan, gain)


def bass(note, t0, length, gain):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = midi(note)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    sig *= np.minimum(1, t / 0.01) * np.exp(-t / (length * 0.9))
    add(sig, t0, 0, gain)


def kick(t0, gain):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 44 + 90 * np.exp(-t / 0.035)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    add(sig, t0, 0, gain)


def hat(t0, gain, pan=0.25):
    n = int(0.09 * SR)
    noise = np.diff(rng.standard_normal(n + 1))
    sig = noise * np.exp(-np.arange(n) / SR / 0.025)
    add(sig, t0, pan, gain)


def tick(t0, gain):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * 1350 * t) + 0.5 * np.sin(2 * np.pi * 2710 * t)) * np.exp(-t / 0.012)
    add(sig, t0, 0.35, gain)


def riser(t_end, length, gain):
    n = int(length * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    a = np.linspace(0.01, 0.35, n)  # one-pole low-pass opening up
    y = 0.0
    for i in range(0, n, 64):
        blk = noise[i:i + 64]
        for j, x in enumerate(blk):
            y += a[i + j] * (x - y)
            out[i + j] = y
    out *= np.linspace(0, 1, n) ** 2
    add(out, t_end - length, -0.2, gain)
    add(out, t_end - length, 0.2, gain * 0.8)


def boom(t0, gain):
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    f = 34 + 40 * np.exp(-t / 0.08)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    add(sig, t0, 0, gain)


def chords_over(names, t0, t1, bars_each, cutoff, gain):
    t, i = t0, 0
    out = []
    while t < t1 - 1e-6:
        length = min(bars_each * BAR, t1 - t)
        name = names[i % len(names)]
        pad(name, t, length, cutoff, gain)
        out.append((name, t, length))
        t += length
        i += 1
    return out


def arp(chordlist, step, pattern, gain, decay, octave=12, bright=0.35):
    for name, t0, length in chordlist:
        notes, _ = CH[name]
        tones = [n + octave for n in notes]
        t, i = t0, 0
        while t < t0 + length - 1e-6:
            pluck(tones[pattern[i % len(pattern)]], t, decay, gain, -0.35 if i % 2 else 0.35, bright)
            t += step
            i += 1


def bassline(chordlist, step, gain):
    for name, t0, length in chordlist:
        root = CH[name][1]
        t = t0
        while t < t0 + length - 1e-6:
            bass(root, t, step, gain)
            t += step


def grid(t0, t1, step):
    t = t0
    while t < t1 - 1e-6:
        yield t
        t += step


# ----------------------------------------------------------------------------
# The arc
# ----------------------------------------------------------------------------
p_end = S["Beat 3"]
problem = chords_over(["Bm", "G", "Em", "F#"], 0.0, p_end, 2, 900, 1.0)
for t in grid(0.0, p_end, BEAT):
    tick(t, 0.05)                                            # the clock: more queue than hours
for t in grid(S["Beat 2"], p_end, BEAT * 2):
    bass(CH["Bm"][1] if t < p_end - 2 * BAR else CH["F#"][1], t, BEAT * 1.8, 0.16)
riser(p_end, 2 * BAR, 0.05)

reveal = chords_over(["G", "Asus", "A"], p_end, S["Beat 4"], 1, 2400, 1.1)
boom(p_end, 0.55)
arp(reveal, BEAT / 2, [0, 1, 2, 3, 2, 1], 0.06, 0.35, 12, 0.2)

swarm = chords_over(["D", "A", "Bm", "G"], S["Beat 4"], S["Transition"], 1, 1800, 1.0)
arp(swarm, BEAT / 2, [0, 2, 1, 3, 2, 1, 3, 2], 0.07, 0.25)
for t in grid(S["Beat 4"], S["Transition"], BAR):
    kick(t, 0.22)
bassline(swarm, BEAT * 2, 0.14)

build = chords_over(["Bm", "A"], S["Transition"], S["Beat 5"], 1, 2200, 1.0)
arp(build, BEAT / 4, [0, 1, 2, 3], 0.05, 0.16)
for t in grid(S["Transition"], S["Beat 5"], BEAT / 2):
    hat(t, 0.025)
riser(S["Beat 5"], S["Beat 5"] - S["Transition"], 0.05)

walk = chords_over(["D", "A", "Bm", "G"], S["Beat 5"], S["Beat 9"], 1, 2000, 0.9)
arp(walk, BEAT / 4, [0, 2, 1, 3, 2, 1, 3, 1], 0.055, 0.14)
bassline(walk, BEAT / 2, 0.10)
for t in grid(S["Beat 5"], S["Beat 9"], BEAT):
    kick(t, 0.22)
for t in grid(S["Beat 5"] + BEAT / 2, S["Beat 9"], BEAT):
    hat(t, 0.03)
for sec in ("Beat 6", "Beat 7", "Beat 8"):                # a soft lift at each new team
    boom(S[sec], 0.18)

drop = chords_over(["G", "Asus"], S["Beat 9"], S["Beat 10"], 1, 1200, 1.0)
arp(drop, BEAT, [0, 2, 3, 1], 0.05, 0.6, 12, 0.15)

close_end = DUR - 1.0
close = chords_over(["D", "A", "Bm", "G"], S["Beat 10"], close_end - 2 * BAR, 1, 2600, 1.0)
close += chords_over(["D"], close_end - 2 * BAR, close_end, 2, 2600, 1.1)
boom(S["Beat 10"], 0.4)
arp(close[:-1], BEAT / 4, [0, 2, 1, 3, 2, 1, 3, 1], 0.055, 0.15)
bassline(close[:-1], BEAT / 2, 0.10)
for t in grid(S["Beat 10"], close_end - 2 * BAR, BEAT):
    kick(t, 0.22)
for t in grid(S["Beat 10"] + BEAT / 2, close_end - 2 * BAR, BEAT):
    hat(t, 0.03)
pluck(CH["D"][0][0] + 12, close_end - 2 * BAR, 1.2, 0.12, 0)  # final ring
boom(close_end - 2 * BAR, 0.35)

# ----------------------------------------------------------------------------
# Room: a short synthetic reverb, then a gentle fade at both ends.
# ----------------------------------------------------------------------------
def reverb(x, seed):
    ir_n = int(2.2 * SR)
    g = np.random.default_rng(seed)
    ir = g.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.55)
    ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + ir_n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y


# Section loudness: quiet under the problem, lift on the reveal, drop under beat 9.
LEVELS = [("Beat 1", -5), ("Beat 3", 0), ("Beat 4", -2.5), ("Transition", -1.5), ("Beat 5", 0),
          ("Beat 9", -6), ("Beat 10", 0)]
curve = np.zeros(N)
for i, (sec, db) in enumerate(LEVELS):
    a = int(S[sec] * SR) if i else 0
    b = int(S[LEVELS[i + 1][0]] * SR) if i + 1 < len(LEVELS) else N
    curve[a:b] = db
k = int(0.6 * SR)
curve = np.convolve(np.pad(curve, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
L *= 10 ** (curve / 20)
R *= 10 ** (curve / 20)

# Keep the sub out of the way of the voice and the room: high-pass at about 35 Hz.
def highpass(x, fc=35.0):
    a = np.exp(-2 * np.pi * fc / SR)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (f / np.sqrt(f ** 2 + fc ** 2)), len(x))


L, R = highpass(L), highpass(R)

wetL, wetR = reverb(L, 1), reverb(R, 2)
L = L + 0.28 * wetL
R = R + 0.28 * wetR
fade = np.ones(N)
fade[: int(0.4 * SR)] = np.linspace(0, 1, int(0.4 * SR))
fade[-int(2.5 * SR):] = np.linspace(1, 0, int(2.5 * SR)) ** 1.5
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.89, R / peak * 0.89

pcm = (np.stack([L, R], axis=1) * 32767).astype("<i2")
with wave.open(str(HERE / "score.wav"), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote score.wav, {DUR:.1f}s")
