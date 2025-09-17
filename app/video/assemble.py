import os, subprocess, math, tempfile, wave
import pathlib
from pathlib import Path
import soundfile as sf

def audio_duration_sec(wav_path: str) -> float:
    data, samplerate = sf.read(wav_path)
    return len(data) / float(samplerate)

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


def concat_videos_ffmpeg(mp4_list, out_path, target_width=960, target_height=540):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    processed_files = []

    # Define standardized parameters for re-encoding
    standard_video_codec = "libx264"
    standard_audio_codec = "aac"
    standard_framerate = "30"
    standard_sample_rate = "44100"

    for video in mp4_list:
        # Check if video has audio
        has_audio = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
             "stream=codec_type", "-of", "csv=p=0", video],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ).stdout.strip() != ""

        if not has_audio:
            # Get video duration
            duration_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video
            ]
            duration = subprocess.run(duration_cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True).stdout.strip()

            # Add silent audio with aspect ratio preservation
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            subprocess.run([
                "ffmpeg", "-y", "-i", video,
                "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={standard_sample_rate}:duration={duration}",
                "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2",
                "-c:v", standard_video_codec, "-r", standard_framerate,
                "-pix_fmt", "yuv420p",
                "-c:a", standard_audio_codec, "-ar", standard_sample_rate,
                "-vsync", "cfr",
                "-map", "0:v", "-map", "1:a",
                temp_video
            ], check=True)
            processed_files.append(temp_video)
        else:
            # Re-encode with aspect ratio preservation
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            subprocess.run([
                "ffmpeg", "-y", "-i", video,
                "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2",
                "-c:v", standard_video_codec, "-r", standard_framerate,
                "-pix_fmt", "yuv420p",
                "-c:a", standard_audio_codec, "-ar", standard_sample_rate,
                "-vsync", "cfr",
                temp_video
            ], check=True)
            processed_files.append(temp_video)

    # Create concat list
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        for p in processed_files:
                tf.write(f"file '{Path(p).resolve().as_posix()}'\n")
        list_path = tf.name

    # Concatenate all videos
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-movflags", "faststart", out_path
    ], check=True)

    # Cleanup temporary files
    for p in processed_files:
        if p not in mp4_list:  # delete only generated ones
            os.remove(p)
    os.remove(list_path)

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
    cmd = ["ffmpeg", "-y", "-i", in_mp4, "-vf", filter_str + ",pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", out_mp4]
    subprocess.run(cmd, check=True)
    return out_mp4
