import os, subprocess, math, tempfile, wave
import pathlib

def audio_duration_sec(wav_path:str) -> float:
    with wave.open(wav_path, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def write_srt(text:str, audio_wav:str, srt_path:str):
    dur = max(0.1, audio_duration_sec(audio_wav))
    # naive: split into N chunks ~5s or by punctuation
    import textwrap, datetime as dt
    words = text.split()
    if not words:
        open(srt_path, "w").close(); return srt_path
    avg_wps = max(2, int(len(words)/max(1,dur)))  # rough words/sec
    chunks = []
    cur = []
    count=0
    for w in words:
        cur.append(w); count += 1
        if count >= avg_wps*4 or w.endswith(('.', '!', '?', ',')):
            chunks.append(' '.join(cur)); cur=[]; count=0
    if cur: chunks.append(' '.join(cur))

    seg_dur = dur / len(chunks)
    def fmt(t):
        ms = int(t*1000)
        hh = ms//3600000; ms-=hh*3600000
        mm = ms//60000; ms-=mm*60000
        ss = ms//1000; ms-=ss*1000
        return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, 1):
            start = seg_dur*(i-1)
            end = seg_dur*i - 0.05
            f.write(f"{i}\n{fmt(start)} --> {fmt(max(start+0.1, end))}\n{chunk}\n\n")
    return srt_path

def concat_videos_ffmpeg(mp4_list, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        for p in mp4_list:
            tf.write(f"file '{os.path.abspath(p)}'\n")
        list_path = tf.name
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
           "-c", "copy", out_path]
    subprocess.run(cmd, check=True)
    return out_path

def burn_subtitles_and_watermark(in_mp4, srt_path, watermark_text, out_mp4):
    # Build filter graph
    vf = []
    if srt_path and os.path.exists(srt_path) and os.path.getsize(srt_path)>0:
        # Ensure forward slashes for ffmpeg compatibility, even on Windows
        ffmpeg_srt_path = pathlib.Path(srt_path).as_posix()
        vf.append(f"subtitles='{ffmpeg_srt_path}'")
    if watermark_text:
        # bottom-right drawtext
        vf.append(f"drawtext=text='{watermark_text}':x=w-tw-20:y=h-th-10:fontcolor=white:alpha=0.6:fontsize=20:box=1:boxcolor=black@0.3:boxborderw=5")
    filter_str = ",".join(vf) if vf else "null"
    cmd = ["ffmpeg", "-y", "-i", in_mp4, "-vf", filter_str, "-c:a", "copy", out_mp4]
    subprocess.run(cmd, check=True)
    return out_mp4
