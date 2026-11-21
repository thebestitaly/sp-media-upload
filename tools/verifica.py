# -*- coding: utf-8 -*-
"""Controlla il piano editoriale prima di pubblicarlo o di aggiungere un nuovo ciclo.

Uso:
  python3 tools/verifica.py                      # controlla data/registro.json
  python3 tools/verifica.py --nuovi nuovi.json   # controlla anche un ciclo nuovo contro il registro
  python3 tools/verifica.py --temi data/ciclo2_temi.json

Blocca (errore): ID o temi doppi, titoli doppi, caption troppo simili, caption oltre 2200 caratteri,
più di 30 hashtag, date fuori da martedì/giovedì/sabato, due contenuti nello stesso giorno.
Segnala (avviso): stessa foto principale entro 28 giorni, tre formati uguali di fila, rubriche sbilanciate nel mese."""
import json, re, sys, datetime as dt
from collections import Counter, defaultdict

ROOT = __file__.rsplit("/tools/", 1)[0]
SIM_MAX = 0.45      # somiglianza massima tra due caption (parole, 4-grammi)
FOTO_GIORNI = 28    # distanza minima tra due usi della stessa foto principale

def norm(s): return re.sub(r"[^a-z0-9àèéìòù ]+", " ", s.lower()).split()

def shingles(text, siti):
    t = text
    for f in siti: t = t.replace(f, " ")  # le frasi del sito si ripetono per scelta: non contano
    w = norm(t.split("\n\n#")[0])
    return {" ".join(w[i:i + 4]) for i in range(max(0, len(w) - 3))}

def jacc(a, b): return len(a & b) / len(a | b) if a and b else 0.0

def main():
    args = sys.argv[1:]
    reg = json.load(open(f"{ROOT}/data/registro.json", encoding="utf-8"))
    posts = reg["contenuti"]
    if "--nuovi" in args:
        posts = posts + json.load(open(args[args.index("--nuovi") + 1], encoding="utf-8"))
    siti = reg.get("frasi_sito", [])
    err, warn = [], []

    for key, label in (("id", "ID"), ("theme", "tema"), ("date", "data")):
        for k, c in Counter(p[key] for p in posts).items():
            if c > 1: err.append(f"{label} doppio: {k}")
    for k, c in Counter(" ".join(norm(p["title"])) for p in posts).items():
        if c > 1: err.append(f"titolo doppio: {k}")

    for p in posts:
        d = dt.date.fromisoformat(p["date"])
        if d.weekday() not in (1, 3, 5): err.append(f"{p['id']}: {p['date']} non è martedì, giovedì o sabato")
        full = p["caption"] + "\n\n" + " ".join(p["tags_full"])
        if len(full) > 2200: err.append(f"{p['id']}: caption di {len(full)} caratteri (max 2200)")
        if len(p["tags_full"]) > 30: err.append(f"{p['id']}: più di 30 hashtag")

    sh = [(p["id"], shingles(p["caption"], siti)) for p in posts]
    for i in range(len(sh)):
        for j in range(i + 1, len(sh)):
            s = jacc(sh[i][1], sh[j][1])
            if s > SIM_MAX: err.append(f"caption troppo simili ({s:.2f}): {sh[i][0]} e {sh[j][0]}")

    last = {}
    for p in sorted(posts, key=lambda x: x["date"]):
        if not p.get("photos"): continue
        f, d = p["photos"][0], dt.date.fromisoformat(p["date"])
        if f in last and (d - last[f][1]).days < FOTO_GIORNI:
            warn.append(f"foto principale {f} ripetuta dopo {(d - last[f][1]).days} giorni: {last[f][0]} → {p['id']}")
        last[f] = (p["id"], d)

    seq = sorted(posts, key=lambda x: x["date"])
    for a, b, c in zip(seq, seq[1:], seq[2:]):
        if a["fmt"] == b["fmt"] == c["fmt"]: warn.append(f"tre {a['fmt']} di fila da {a['id']}")
    m = defaultdict(Counter)
    for p in posts: m[p["date"][:7]][p["pillar"]] += 1
    for mese, c in sorted(m.items()):
        if sum(c.values()) < 12: continue  # mesi parziali (riavvio)
        if max(c.values()) - min(c.values()) > 2 or len(c) < 7:
            warn.append(f"{mese}: rubriche sbilanciate {dict(c)}")

    if "--temi" in args:
        temi = json.load(open(args[args.index("--temi") + 1], encoding="utf-8"))["temi"]
        usati = {p["theme"] for p in posts}
        for t in temi:
            if t["theme"] in usati: err.append(f"tema del ciclo successivo già usato: {t['theme']}")
        for k, c in Counter(t["theme"] for t in temi).items():
            if c > 1: err.append(f"tema doppio nella banca: {k}")

    print(f"Contenuti controllati: {len(posts)}")
    for e in err: print("ERRORE ", e)
    for w in warn: print("avviso ", w)
    print("OK, nessun errore." if not err else f"{len(err)} errori da correggere.")
    sys.exit(1 if err else 0)

if __name__ == "__main__":
    main()
