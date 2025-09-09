import subprocess
import os
import json
import tempfile
import shutil
import argparse

def get_video_duration(video_path):
    """Gets the duration of a video in seconds using ffprobe."""
    try:
        probe = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ], capture_output=True, text=True, check=True)
        return float(probe.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        print(f"Warning: Could not get duration for {video_path}. Assuming 0.")
        return 0.0

def _pad_video(input_path, target_duration, temp_output_path):
    """
    Pads a video (video stream with last frame, audio with silence) to a target duration.
    If video is already long enough, it's just copied.
    """
    current_duration = get_video_duration(input_path)

    if current_duration >= target_duration:
        shutil.copyfile(input_path, temp_output_path)
        return

    pad_duration = target_duration - current_duration

    # Check for audio stream
    audio_probe = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_type", "-of", "csv=p=0", input_path
    ], capture_output=True, text=True)
    has_audio = audio_probe.stdout.strip() == "audio"

    filter_complex = f"[0:v]tpad=stop_mode=clone:stop_duration={pad_duration}[v_padded]"
    map_options = ["-map", "[v_padded]"]

    if has_audio:
        # Get audio sample rate for apad
        sr_probe = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate", "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ], capture_output=True, text=True)
        sample_rate = sr_probe.stdout.strip() if sr_probe.stdout.strip() else "44100"

        filter_complex += f";[0:a]apad=whole_dur={target_duration}[a_padded]"
        map_options.extend(["-map", "[a_padded]"])
    else:
        # If no audio, add a silent audio track for the entire target duration
        filter_complex += f";anullsrc=channel_layout=stereo:sample_rate=44100:duration={target_duration}[a_padded]"
        map_options.extend(["-map", "[a_padded]"])

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter_complex", filter_complex,
        *map_options,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        temp_output_path
    ]
    subprocess.run(cmd, check=True)


def side_by_side_videos(video1_path, video2_path, output_path):
    """
    Combines two videos side-by-side. If one video is shorter,
    its last frame is held static and audio padded with silence.
    """
    temp_files = []
    try:
        duration1 = get_video_duration(video1_path)
        duration2 = get_video_duration(video2_path)
        max_duration = max(duration1, duration2)

        # Pad video 1
        temp_video1_padded = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        temp_files.append(temp_video1_padded)
        print(f"Padding/Processing video 1: {video1_path}")
        _pad_video(video1_path, max_duration, temp_video1_padded)

        # Pad video 2
        temp_video2_padded = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        temp_files.append(temp_video2_padded)
        print(f"Padding/Processing video 2: {video2_path}")
        _pad_video(video2_path, max_duration, temp_video2_padded)

        # Combine padded videos side-by-side with merged audio
        print("Combining videos side by side...")
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_video1_padded,
            "-i", temp_video2_padded,
            "-filter_complex",
            "[0:v][1:v]hstack=inputs=2[v_out];"
            "[0:a][1:a]amerge=inputs=2[a_out]",
            "-map", "[v_out]",
            "-map", "[a_out]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", # Ensure output doesn't exceed padded audio duration
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Successfully created side-by-side video: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error during video processing: {e}")
        print(f"FFmpeg stderr: {e.stderr.decode()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up temporary files
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
        print("Cleaned up temporary files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine two videos side-by-side, padding shorter videos with static last frame and silent audio.")
    parser.add_argument("--vid1", required=True, help="Path to the first input video.")
    parser.add_argument("--vid2", required=True, help="Path to the second input video.")
    parser.add_argument("--output", required=True, help="Path for the output side-by-side video.")

    args = parser.parse_args()

    side_by_side_videos(args.video1_path, args.video2_path, args.output_path)
