"""Brani strumentali originali per i reel Space Pillow, sintetizzati da zero (nessun campione esterno)."""
import numpy as np, scipy.signal as ss, soundfile as sf, sys, os
SR = 44100
rng = np.random.default_rng(7)
NOTES = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
def hz(n):
    name, octv = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((NOTES[name] + 12 * (octv + 1) - 69) / 12)

def t_(d): return np.arange(int(d * SR)) / SR

def adsr(n, a=0.005, r=0.05):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return e

def partials(f, d, spec, attack=0.003):
    t = t_(d); y = np.zeros_like(t)
    for ratio, amp, tau in spec:
        fr = f * ratio
        if fr > SR / 2.2: continue
        y += amp * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    return y * adsr(len(t), attack, 0.03)

def musicbox(f, d): return partials(f, max(d, 2.2), [(1, 1, 1.1), (2, .22, .45), (3, .08, .25), (5.8, .05, .06), (9.6, .03, .02)], .002)
def glock(f, d):    return partials(f, max(d, 1.8), [(1, 1, .9), (2.76, .32, .35), (5.4, .14, .12), (8.93, .06, .05)], .001)
def celesta(f, d):  return partials(f, max(d, 1.6), [(1, 1, .8), (2, .18, .3), (4, .1, .15), (10, .03, .03)], .002)
def epiano(f, d):
    spec = [(1, 1, 1.6), (2, .35, .9), (3, .12, .5), (4, .06, .3), (14, .02, .02)]
    y = partials(f, d + .4, spec, .004); n = int(d * SR); r = len(y) - n
    if r > 0: y[n:] *= np.linspace(1, 0, r)
    return y
def piano(f, d):
    B = .0003; spec = [(k * np.sqrt(1 + B * k * k), 1 / k ** 1.3, 2.2 / k ** .6) for k in range(1, 11)]
    y = partials(f, d + .5, spec, .004); n = int(d * SR)
    if len(y) > n: y[n:] *= np.linspace(1, 0, len(y) - n)
    return y
def pad(f, d):
    t = t_(d + 1.2); y = np.zeros_like(t)
    for det in (-0.12, 0, 0.11):
        for k in range(1, 9):
            y += (1 / k ** 1.8) * np.sin(2 * np.pi * f * (1 + det / 100) * k * t + rng.uniform(0, 6.28))
    e = np.minimum(1, t / 1.0) * np.where(t > d, np.exp(-(t - d) / .4), 1)
    return y * e * (1 + .08 * np.sin(2 * np.pi * .3 * t)) / 3
def bass(f, d):
    t = t_(d + .1); y = np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)
    return y * np.exp(-t / max(.35, d * .6)) * adsr(len(t), .006, .06)
def pluck(f, d):
    """Karplus-Strong vettorizzato a blocchi."""
    n = int((d + 1.2) * SR); N = int(SR / f); y = np.zeros(n + N)
    y[:N] = rng.uniform(-1, 1, N); y[:N] = np.convolve(y[:N], np.ones(4) / 4, 'same')
    k = N
    while k < n + N:
        e = min(k + N, n + N); prev = y[k - N:e - N + 1]
        if len(prev) < e - k + 1: prev = np.append(prev, prev[-1])
        y[k:e] = .996 * .5 * (prev[:e - k] + prev[1:e - k + 1]); k = e
    y = y[:n]; nd = int(d * SR)
    if n > nd: y[nd:] *= np.exp(-np.arange(n - nd) / (.25 * SR))
    return y
def kick(_f=0, _d=0):
    t = t_(.35); f = 45 + 75 * np.exp(-t / .04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .12)
def noiseburst(d, lo, hi, tau):
    t = t_(d); x = rng.standard_normal(len(t))
    b, a = ss.butter(2, [lo / (SR / 2), min(hi, SR / 2.2) / (SR / 2)], 'band')
    return ss.lfilter(b, a, x) * np.exp(-t / tau)
def shaker(_f=0, _d=0): return noiseburst(.09, 5000, 12000, .025) * .6
def snap(_f=0, _d=0):   return noiseburst(.18, 1200, 6000, .045)
def sleigh(_f=0, _d=0):
    y = noiseburst(.22, 6000, 14000, .06); t = t_(.22)
    return y * (1 + .6 * np.sin(2 * np.pi * 38 * t))

INSTR = dict(musicbox=musicbox, glock=glock, celesta=celesta, epiano=epiano, piano=piano, pad=pad,
             bass=bass, pluck=pluck, kick=kick, shaker=shaker, snap=snap, sleigh=sleigh)

class Track:
    def __init__(s, bpm, seconds):
        s.bpm = bpm; s.beat = 60 / bpm; s.L = np.zeros((int((seconds + 4) * SR), 2)); s.W = np.zeros_like(s.L); s.seconds = seconds; s.stems = {}; s.gain = {}
    def add(s, beat, note, dur, inst, vel=1.0, pan=0.0, wet=.3):
        f = hz(note) if isinstance(note, str) else note
        y = INSTR[inst](f, dur * s.beat) * vel * s.gain.get(inst, 1.0)
        i = int(beat * s.beat * SR + rng.normal(0, 0.003) * SR * (inst not in ('kick',)))
        i = max(0, i); y = y[:len(s.L) - i]
        g = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)])
        st = s.stems.setdefault(inst, np.zeros(len(s.L))); st[i:i + len(y)] += y
        s.L[i:i + len(y)] += y[:, None] * g * (1 - wet * .5); s.W[i:i + len(y)] += y[:, None] * g * wet
    def chord(s, beat, notes, dur, inst, vel=.5, pan=0, wet=.4, strum=0.0):
        for j, n in enumerate(notes): s.add(beat + j * strum, n, dur, inst, vel, pan + (j - len(notes) / 2) * .15, wet)
    def render(s, path, rt=2.4):
        n = int(rt * SR); t = np.arange(n) / SR
        ir = np.stack([rng.standard_normal(n) * np.exp(-t / (rt / 6.9)) for _ in range(2)], 1)
        b, a = ss.butter(1, 5000 / (SR / 2)); ir = ss.lfilter(b, a, ir, axis=0); ir[:int(.012 * SR)] = 0
        ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
        wet = np.stack([ss.fftconvolve(s.W[:, c], ir[:, c])[:len(s.W)] for c in range(2)], 1) * 0.9
        y = s.L + wet
        s.stat = {k: 20*np.log10(np.sqrt((v**2).mean())+1e-12) for k, v in s.stems.items()}
        y = y[:int((s.seconds + 3) * SR)]
        fo = int(3 * SR); y[-fo:] *= np.linspace(1, 0, fo)[:, None]
        y = y / (np.abs(y).max() + 1e-9); y = np.tanh(1.1 * y) / np.tanh(1.1); y *= .89
        sf.write(path, y, SR); return path
