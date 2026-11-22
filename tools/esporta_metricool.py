# -*- coding: utf-8 -*-
"""Genera il CSV per l'importazione massiva in Metricool dal registro dei contenuti.

Uso:
  python3 tools/esporta_metricool.py --base https://UTENTE.github.io/REPO/ [--reti instagram,facebook] [--bozze no] [--tieni-bozze SP-C1-063,SP-C1-077]

- Colonne identiche al modello CSV di Metricool (101 colonne).
- Date: YYYY-MM-DD, orari: HH:MM:SS (in Metricool, al momento dell'import, scegliere questi due formati).
- Caroselli: un'immagine per colonna (Picture Url 1…10). Reel: il video in Picture Url 1 e la copertina in Video Thumbnail Url.
- Per impostazione i contenuti entrano come bozze (Draft = TRUE): si approvano in Metricool dopo aver aggiunto l'audio ai reel.
"""
import csv, json, sys

ROOT = __file__.rsplit("/tools/", 1)[0]
COLS = "Text,Date,Time,Draft,Facebook,Twitter/X,LinkedIn,GBP,Instagram,Pinterest,TikTok,Youtube,Threads,Bluesky,Picture Url 1,Picture Url 2,Picture Url 3,Picture Url 4,Picture Url 5,Picture Url 6,Picture Url 7,Picture Url 8,Picture Url 9,Picture Url 10,Alt text picture 1,Alt text picture 2,Alt text picture 3,Alt text picture 4,Alt text picture 5,Alt text picture 6,Alt text picture 7,Alt text picture 8,Alt text picture 9,Alt text picture 10,Document title,Shortener,Video Thumbnail Url,Video Cover Frame,Twitter/X Can reply,Twitter/X Type,Twitter/X Poll Duration minutes,Twitter/X Poll Option 1,Twitter/X Poll Option 2,Twitter/X Poll Option 3,Twitter/X Poll Option 4,Pinterest Board,Pinterest Pin Title,Pinterest Pin Link,Pinterest Pin New Format,Pinterest AI generated content,Pinterest AI generated person,Instagram Post Type,Instagram Show Reel On Feed,Instagram Trial Reel Share Automatically,Instagram Paid Partnership,Instagram Paid Partnership Brands,Youtube Video Title,Youtube Video Type,Youtube Video Privacy,Youtube video for kids,Youtube AI generated content,Youtube notify subscribers,Youtube Video Category,Youtube Video Tags,Youtube playlist,GBP Post Type,Facebook Post Type,Facebook Title,First Comment Text,TikTok Title,TikTok disable comments,TikTok disable duet,TikTok disable stitch,TikTok Post Privacy,TikTok Branded Content,TikTok Your Brand,TikTok Auto Add Music,TikTok Photo Cover Index,TikTok musicId,TikTok music title,TikTok music author,TikTok music previewUrl,TikTok music thumbnailUrl,TikTok music soundVolume,TikTok music originalVolume,TikTok music startMillis,TikTok music endMillis,TikTok is AI generated content,LinkedIn Type,LinkedIn Poll Question,LinkedIn Poll Option 1,LinkedIn Poll Option 2,LinkedIn Poll Option 3,LinkedIn Poll Option 4,LinkedIn Poll Duration,LinkedIn Show link preview,LinkedIn Images as Carousel,Threads Reply Control,Threads Is Spoiler,Threads Post Type,Tags".split(",")

def arg(name, default=None):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default

def main():
    base = arg("--base")
    if not base: sys.exit("Indica l'indirizzo di GitHub Pages con --base https://UTENTE.github.io/REPO/")
    base = base.rstrip("/") + "/"
    reti = [r.strip().lower() for r in arg("--reti", "instagram").split(",")]
    bozze = arg("--bozze", "si").lower() not in ("no", "false", "0")
    tieni = set(x.strip() for x in arg("--tieni-bozze", "").split(",") if x.strip())
    out = arg("--out", f"{ROOT}/metricool/space-pillow_metricool.csv")
    reg = json.load(open(f"{ROOT}/data/registro.json", encoding="utf-8"))["contenuti"]
    rows = []
    for p in reg:
        r = {c: "" for c in COLS}
        r["Text"] = p["caption"] + "\n\n" + " ".join(p["tags_full"])
        r["Date"] = p["date"]; r["Time"] = p["time"] + ":00"
        r["Draft"] = "TRUE" if (bozze or p["id"] in tieni) else "FALSE"
        for net, col in (("instagram", "Instagram"), ("facebook", "Facebook")):
            r[col] = "TRUE" if net in reti else "FALSE"
        url = lambda f: f"{base}media/{p['folder']}/{f}"
        files = p["files"][:10]
        for i, f in enumerate(files, 1):
            r[f"Picture Url {i}"] = url(f)
            if not f.endswith(".mp4"): r[f"Alt text picture {i}"] = f"{p['title']} – Space Pillow ({i}/{len(files)})" if len(files) > 1 else f"{p['title']} – Space Pillow"
        if p["fmt"] == "reel":
            r["Video Thumbnail Url"] = url(p["cover"])
            r["Instagram Post Type"] = "REEL"; r["Instagram Show Reel On Feed"] = "TRUE"
            if "facebook" in reti: r["Facebook Post Type"] = "REEL"
        else:
            r["Instagram Post Type"] = "POST"
            if "facebook" in reti: r["Facebook Post Type"] = "POST"
        r["Tags"] = f"{p['id']};{p['pillar']}"
        rows.append(r)
    import os; os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_MINIMAL); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} righe → {out}")

if __name__ == "__main__":
    main()
