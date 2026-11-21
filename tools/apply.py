"""Inserisce i brani di marca nei reel senza audio. Idempotente: parte sempre dagli originali muti in reels_muti/."""
import os, shutil, subprocess, json
RL = "/home/claude/work/out/reels"; BK = "/home/claude/work/out/reels_muti"; MU = "/home/claude/work/music/out"
MAP = {
 'ninna':     ['05', '23', '32', '33', '51', '62', '67', '75'],
 'avventura': ['R1', '01', '29', '47', '71'],
 'prodotto':  ['22', '25', '44', '56', '61', '69', '73'],
 'natale':    ['09', '14', '16'],
 'famiglie':  ['40', '54', '77'],
}
def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
os.makedirs(BK, exist_ok=True)
for track, codes in MAP.items():
    for c in codes:
        src = f"{RL}/reel_{c}.mp4"; bk = f"{BK}/reel_{c}.mp4"
        if not os.path.exists(bk): shutil.copy(src, bk)
        d = dur(bk); fo = min(1.5, d * .12)
        af = f"atrim=0:{d:.3f},afade=t=in:d=0.15,afade=t=out:st={d - fo:.3f}:d={fo:.3f}"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', bk, '-i', f"{MU}/{track}_master.wav", '-map', '0:v:0', '-map', '1:a:0',
                        '-c:v', 'copy', '-af', af, '-c:a', 'aac', '-b:a', '112k', '-ar', '44100', '-ac', '2', '-shortest',
                        '-movflags', '+faststart', src], check=True)
        print(c, track, round(d, 2), '→', round(dur(src), 2))
