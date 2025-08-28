import os, pathlib, subprocess, sys
from app.utils.io import load_spec, ensure_dir
from app.audio.tts import synthesize
from app.video.montage import ken_burns_clip
from app.video.talking_head import generate_talking_head
from app.video.assemble import write_srt, burn_subtitles_and_watermark, concat_videos_ffmpeg
from app.video.compress import normalize_and_compress

def run_project(spec_path, out_path, workdir):
    spec = load_spec(spec_path)
    ensure_dir(workdir)
    tmp = pathlib.Path(workdir)

    fps = spec.get("output", {}).get("fps", 25)
    res = spec.get("output", {}).get("resolution", "960x540")
    width, height = [int(x) for x in res.lower().split("x")]
    target_size_mb = spec.get("output", {}).get("target_size_mb", 3)
    watermark = spec.get("watermark", "")

    scene_mp4s = []
    for scene in spec["scenes"]:
        sid = scene["id"]
        mode = scene.get("mode", "narration")
        duration = float(scene.get("duration_sec", 6))
        script_text = scene.get("script_text", "")
        voice = scene.get("voice", {})

        # 1) Audio
        audio_wav = str(tmp / f"{sid}.wav")
        synthesize(script_text, audio_wav, engine=voice.get("engine","piper"), voice=voice.get("voice"))

        # 2) Video per mode
        raw_mp4 = str(tmp / f"{sid}_raw.mp4")
        if mode == "narration":
            images = scene.get("images", [])
            ken_burns_clip(images, raw_mp4, audio_wav,duration_sec=duration, fps=fps, size=(width, height))
        elif mode == "talking_head":
            portrait = scene["portrait"]
            engine = scene.get("lipsync_engine", "wav2lip")
            generate_talking_head(portrait, audio_wav, raw_mp4, engine=engine)
        else:
            raise ValueError(f"Unknown scene mode: {mode}")

        # 3) Subtitles + watermark (optional)
        final_scene = raw_mp4
        if spec.get("subtitles", False) or watermark:
            srt = None
            if spec.get("subtitles", False):
                srt = str(tmp / f"{sid}.srt")
                write_srt(script_text, audio_wav, srt)
            burned = str(tmp / f"{sid}_burned.mp4")
            burn_subtitles_and_watermark(raw_mp4, srt, watermark, burned)
            final_scene = burned

        scene_mp4s.append(final_scene)

    # 4) Concat scenes
    merged = str(tmp / "merged.mp4")
    concat_videos_ffmpeg(scene_mp4s, merged)

    # 5) Compress to target
    normalize_and_compress(merged, out_path, width=width, height=height, fps=fps, target_size_mb=target_size_mb, two_pass=True)

    print(f"[DONE] Wrote {out_path}")
    return out_path
