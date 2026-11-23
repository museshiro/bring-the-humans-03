#!/usr/bin/env python3
"""Synthesize a short upbeat electronic loop (no copyrighted material):
128 BPM, kick on every beat, hats on off-beats, a simple bass line and a
bright two-note sparkle. Written as 16-bit PCM WAV, ~17.3 s."""
import math
import struct
import wave

SR = 44100
DUR = 17.3
BPM = 128
BEAT = 60.0 / BPM  # 0.46875 s

# bass line: one note per beat, A minor-ish groove (Hz)
BASS_NOTES = [110.0, 110.0, 130.81, 98.0, 110.0, 110.0, 146.83, 164.81]

n = int(SR * DUR)
out = [0.0] * n

def add_kick(t0):
    # sine sweep 150 -> 48 Hz with fast decay
    L = min(int(0.28 * SR), n - t0)
    for i in range(L):
        t = i / SR
        f = 48 + (150 - 48) * math.exp(-t * 28)
        phase = 2 * math.pi * f * t
        out[t0 + i] += 0.85 * math.sin(phase) * math.exp(-t * 16)

def add_hat(t0, vol=0.16):
    L = min(int(0.06 * SR), n - t0)
    # deterministic pseudo-noise via a hash of the sample index
    for i in range(L):
        x = (t0 + i) * 2654435761 % 4294967296
        noise = ((x / 4294967296.0) * 2 - 1)
        out[t0 + i] += vol * noise * math.exp(-i / (0.012 * SR))

def add_bass(t0, freq):
    L = min(int(BEAT * 0.92 * SR), n - t0)
    for i in range(L):
        t = i / SR
        out[t0 + i] += 0.30 * math.sin(2 * math.pi * freq * t) * math.exp(-t * 3.5)
        out[t0 + i] += 0.12 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-t * 5)

def add_sparkle(t0, freq):
    L = min(int(0.22 * SR), n - t0)
    for i in range(L):
        t = i / SR
        out[t0 + i] += 0.10 * math.sin(2 * math.pi * freq * t) * math.exp(-t * 12)

beat = 0
bi = 0
while beat < DUR:
    t0 = int(beat * SR)
    add_kick(t0)
    add_bass(t0, BASS_NOTES[bi % len(BASS_NOTES)])
    # hats on the off-beat
    off = t0 + int(BEAT * SR / 2)
    if off < n:
        add_hat(off)
    # sparkle every 2 beats, alternating 880 / 1046.5 Hz
    if bi % 2 == 0:
        add_sparkle(t0, 880.0 if (bi // 2) % 2 == 0 else 1046.5)
    beat += BEAT
    bi += 1

# gentle fade-out over the last 0.5 s + soft limiter
peak = max(abs(v) for v in out) or 1.0
gain = 0.85 / peak
fade = int(0.5 * SR)
for i in range(n):
    v = out[i] * gain
    if i > n - fade:
        v *= (n - i) / fade
    out[i] = v

with wave.open("music.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in out))
print("music.wav written", DUR, "s, peak-normalized")
