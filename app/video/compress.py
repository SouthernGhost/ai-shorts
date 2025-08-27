import os, subprocess, math

def size_target_bitrate(duration_sec, target_size_mb, audio_kbps=64):
    total_bits = target_size_mb * 8 * 1024 * 1024
    audio_bits = audio_kbps*1000 * duration_sec
    video_bits = max(1, total_bits - audio_bits)
    return int(video_bits / duration_sec / 1000)  # kbps

def normalize_and_compress(in_mp4, out_mp4, width=960, height=540, fps=25, target_size_mb=3, two_pass=True):
    # Estimate duration
    import subprocess, json, tempfile
    probe = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                            "-show_entries", "format=duration", in_mp4],
                           capture_output=True, text=True, check=True)
    duration = float(json.loads(probe.stdout)["format"]["duration"])

    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)

    if two_pass:
        b_v = size_target_bitrate(duration, target_size_mb)
        # Pass 1
        cmd1 = [
            "ffmpeg", "-y", "-i", in_mp4,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            "-r", str(fps),
            "-c:v", "libx264", "-b:v", f"{b_v}k",
            "-pass", "1", "-an", "-f", "mp4", os.devnull
        ]
        subprocess.run(cmd1, check=True)
        # Pass 2
        cmd2 = [
            "ffmpeg", "-y", "-i", in_mp4,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            "-r", str(fps),
            "-c:v", "libx264", "-b:v", f"{b_v}k",
            "-pass", "2", "-c:a", "aac", "-b:a", "64k", "-ac", "1",
            "-movflags", "+faststart", out_mp4
        ]
        subprocess.run(cmd2, check=True)
    else:
        cmd = [
            "ffmpeg", "-y", "-i", in_mp4,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            "-r", str(fps),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
            "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "64k", "-ac", "1",
            "-movflags", "+faststart", out_mp4
        ]
        subprocess.run(cmd, check=True)
    return out_mp4
