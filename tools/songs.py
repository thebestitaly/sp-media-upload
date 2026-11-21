"""I cinque brani di marca. Melodie e armonie originali."""
import sys; sys.path.insert(0, '/home/claude/work/music')
from synth import Track, rng
import numpy as np

V = {  # voicing accordi
 'F': ['F3', 'A3', 'C4', 'F4'], 'Dm': ['D3', 'F3', 'A3', 'D4'], 'Bb': ['Bb2', 'D3', 'F3', 'Bb3'], 'C': ['C3', 'E3', 'G3', 'C4'],
 'Am': ['A2', 'E3', 'A3', 'C4'], 'G': ['G2', 'D3', 'G3', 'B3'], 'Em': ['E3', 'G3', 'B3', 'E4'], 'D': ['D3', 'A3', 'D4', 'F#4'],
 'A': ['A2', 'E3', 'A3', 'C#4'], 'Bm': ['B2', 'F#3', 'B3', 'D4']}
def up(n, k=1): return n[:-1] + str(int(n[-1]) + k)
def mel(T, bar0, bars, beats_per_bar, inst, vel, pan=0, wet=.35):
    for b, notes in enumerate(bars):
        pos = 0
        for n, d in notes:
            if n: T.add((bar0 + b) * beats_per_bar + pos, n, d, inst, vel, pan, wet)
            pos += d

def ninna(path):
    T = Track(72, 31); bpb = 3; T.gain = {'bass':.65,'celesta':1.5}
    prog = ['F', 'Dm', 'Bb', 'C', 'F', 'Am', 'Bb', 'C', 'Dm', 'Bb', 'C', 'F']
    for i, c in enumerate(prog):
        T.chord(i * bpb, [up(n) for n in V[c][1:]], 3, 'pad', .10, wet=.5)
        T.add(i * bpb, up(V[c][0], 0 if V[c][0][-1] == '2' else -1), 3, 'bass', .30, 0, .2)
        for k in (1, 2): T.add(i * bpb + k, up(V[c][k], 1), 1, 'celesta', .10, -.3, .45)
    M = [[('A5', 1), ('C6', 1), ('A5', 1)], [('F5', 2), ('D5', 1)], [('D5', 1), ('F5', 1), ('Bb5', 1)], [('A5', 1.5), ('G5', .5), ('E5', 1)],
         [('F5', 1), ('A5', 1), ('C6', 1)], [('E6', 2), ('C6', 1)], [('D6', 1), ('C6', 1), ('Bb5', 1)], [('A5', 2), ('G5', 1)],
         [('F5', 1), ('A5', 1), ('D6', 1)], [('D6', 1.5), ('C6', .5), ('Bb5', 1)], [('G5', 1), ('Bb5', 1), ('E5', 1)], [('F5', 3)]]
    mel(T, 0, M, bpb, 'musicbox', .42, .15, .4)
    for i in range(0, 36, 4):  # stelline
        T.add(i + rng.uniform(0, 2), rng.choice(['F6', 'G6', 'A6', 'C7', 'D7']), .5, 'glock', .06, rng.uniform(-.7, .7), .7)
    return T.render(path, 2.8)

def avventura(path):
    T = Track(112, 30); bpb = 4; T.gain = {'snap':6,'shaker':5}
    prog = ['C', 'G', 'Am', 'F'] * 3 + ['C', 'G', 'C']
    tones = {'C': ['C5', 'E5', 'G5', 'C6'], 'G': ['B4', 'D5', 'G5', 'B5'], 'Am': ['C5', 'E5', 'A5', 'C6'], 'F': ['C5', 'F5', 'A5', 'C6']}
    for i, c in enumerate(prog):
        last = i == len(prog) - 1
        T.chord(i * bpb, [up(n) for n in V[c][1:]], 4, 'pad', .07, wet=.5)
        if last:
            T.chord(i * bpb, tones[c], 4, 'glock', .14, wet=.5); T.add(i * bpb, up(V[c][0], 0), 4, 'pluck', .5, 0, .2); continue
        for k, idx in enumerate([0, 1, 2, 3, 2, 1, 2, 1]): T.add(i * bpb + k * .5, tones[c][idx], .5, 'glock', .13, -.35, .35)
        r = up(V[c][0], 0 if V[c][0][-1] == '2' else -1)
        for p, d in ((0, 1.5), (1.5, .5), (2, 1.5), (3.5, .5)): T.add(i * bpb + p, r, d, 'pluck', .45, 0, .15)
        if i >= 4:
            for p in (0, 2): T.add(i * bpb + p, 0, 1, 'kick', .55, 0, .05)
            for p in (1, 3): T.add(i * bpb + p, 0, 1, 'snap', .16, .1, .25)
        for p in range(8): T.add(i * bpb + p * .5 + .5 * (p % 2 == 0) * 0, 0, 1, 'shaker', .10 if p % 2 else .05, .4, .2)
    M = [[('E5', 1), ('G5', 1), ('C6', 2)], [('B5', 1), ('D6', 1), ('G5', 2)], [('C6', 1), ('B5', .5), ('A5', .5), ('E5', 2)],
         [('F5', 1), ('A5', 1), ('C6', 1), ('A5', 1)], [('G5', 1), ('E6', 1), ('D6', 1), ('C6', 1)], [('D6', 1), ('B5', 1), ('G5', 2)],
         [('A5', 1), ('C6', 1), ('E6', 1), ('D6', 1)], [('C6', 1.5), ('A5', .5), ('F5', 1), ('G5', 1)], [('C6', 4)], [('B5', 2), ('D6', 2)]]
    mel(T, 4, M, bpb, 'celesta', .40, .2, .35)
    return T.render(path, 2.2)

def prodotto(path):
    T = Track(100, 30); bpb = 4; T.gain = {'bass':.6,'epiano':.6,'glock':1.4,'snap':5,'shaker':5}
    prog = ['Am', 'F', 'C', 'G'] * 3 + ['Am']
    top = {'Am': ['E5', 'C5', 'A4'], 'F': ['F5', 'C5', 'A4'], 'C': ['G5', 'E5', 'C5'], 'G': ['G5', 'D5', 'B4']}
    for i, c in enumerate(prog):
        v = [up(n) for n in V[c][1:]]
        if i == len(prog) - 1:
            T.chord(i * bpb, v, 4, 'epiano', .28, wet=.45); T.add(i * bpb, V[c][0], 4, 'bass', .45); continue
        for p, d in ((0, .9), (1.5, .4), (2.5, 1.3)): T.chord(i * bpb + p, v, d, 'epiano', .22, wet=.3)
        r = up(V[c][0], 0 if V[c][0][-1] == '2' else -1)
        for p in range(8): T.add(i * bpb + p * .5, r if p % 4 != 3 else up(r), .45, 'bass', .32 if p % 2 == 0 else .2, 0, .05)
        if i >= 2:
            for p in (0, 2): T.add(i * bpb + p, 0, 1, 'kick', .6, 0, .03)
            for p in (1, 3): T.add(i * bpb + p, 0, 1, 'snap', .2, -.1, .2)
        for p in range(8): T.add(i * bpb + p * .5, 0, 1, 'shaker', .09 if p % 2 else .05, .35, .15)
        if 4 <= i < 12:
            a, b, cc = top[c]
            for p, n in ((0, a), (.75, b), (1.5, cc), (3, b)): T.add(i * bpb + p, up(n), .7, 'glock', .16, .3, .4)
    return T.render(path, 1.8)

def natale(path):
    T = Track(96, 31); bpb = 4; T.gain = {'sleigh':3}
    prog = ['G', 'Em', 'C', 'D', 'G', 'Em', 'Am', 'D', 'G', 'C', 'D', 'G', 'G']
    for i, c in enumerate(prog):
        T.chord(i * bpb, [up(n) for n in V[c][1:]], 4, 'pad', .09, wet=.5)
        r = up(V[c][0], 0 if V[c][0][-1] == '2' else -1)
        if i == len(prog) - 1:
            T.add(i * bpb, r, 4, 'pluck', .5); T.chord(i * bpb, ['G5', 'B5', 'D6', 'G6'], 4, 'glock', .12, wet=.6); continue
        for p in (0, 2): T.add(i * bpb + p, r, 1, 'pluck', .42, -.1, .2)
        for p in (1, 3): T.add(i * bpb + p, up(V[c][2]), 1, 'pluck', .22, .1, .25)
        for p in range(8): T.add(i * bpb + p * .5, 0, 1, 'sleigh', .10 if p % 2 == 0 else .06, .45, .3)
        if i % 2 == 0: T.add(i * bpb, up(V[c][0], 4 - int(V[c][0][-1])), 2, 'glock', .07, -.5, .6)
    M = [[('B5', 1), ('D6', 1), ('B5', 1), ('A5', 1)], [('G5', 2), ('E5', 2)], [('C6', 1), ('B5', 1), ('A5', 1), ('G5', 1)], [('A5', 4)],
         [('B5', 1), ('D6', 1), ('E6', 1), ('D6', 1)], [('B5', 2), ('G5', 2)], [('A5', 1), ('B5', 1), ('A5', 1), ('F#5', 1)], [('A5', 2), ('F#5', 2)],
         [('G5', 1), ('B5', 1), ('D6', 1), ('G6', 1)], [('E6', 2), ('C6', 2)], [('D6', 1), ('C6', 1), ('B5', 1), ('A5', 1)], [('G5', 4)]]
    mel(T, 0, M, bpb, 'celesta', .40, .15, .4)
    return T.render(path, 2.4)

def famiglie(path):
    T = Track(84, 31); bpb = 4; T.gain = {'pluck':2.6}
    prog = ['D', 'A', 'Bm', 'G', 'D', 'A', 'G', 'A', 'Bm', 'G', 'D']
    for i, c in enumerate(prog):
        v = V[c]; last = i == len(prog) - 1
        T.chord(i * bpb, [up(n) for n in v[1:]], 4, 'pad', .05, wet=.5)
        if last:
            T.chord(i * bpb, v, 4, 'pluck', .3, -.2, .3, strum=.06); continue
        for k, idx in enumerate([0, 1, 2, 3, 2, 1, 2, 3]): T.add(i * bpb + k * .5, v[idx] if idx else v[0], .9, 'pluck', .30 if k == 0 else .2, -.3, .3)
    M = [[('F#5', 1), ('A5', 1), ('B5', 1), ('A5', 1)], [('G5', 2), ('D5', 2)], [('F#5', 1), ('E5', .5), ('D5', .5), ('A5', 2)],
         [('E5', 1), ('F#5', 1), ('E5', 1), ('C#5', 1)], [('D5', 1), ('G5', 1), ('B5', 1), ('A5', 1)], [('A5', 3), ('E5', 1)],
         [('F#5', 1), ('D5', 1), ('F#5', 1), ('B5', 1)], [('A5', 1.5), ('G5', .5), ('E5', 2)], [('D5', 4)]]
    mel(T, 2, M, bpb, 'piano', .38, .2, .35)
    return T.render(path, 2.2)

if __name__ == '__main__':
    import os; os.makedirs('/home/claude/work/music/out', exist_ok=True)
    import synth
    orig = synth.Track.render
    def r(self, path, rt=2.4):
        out = orig(self, path, rt); print(path.split('/')[-1], {k: round(v, 1) for k, v in sorted(self.stat.items(), key=lambda x: -x[1])}); return out
    synth.Track.render = r
    for f in (ninna, avventura, prodotto, natale, famiglie): f(f'/home/claude/work/music/out/{f.__name__}.wav')
