import cv2, numpy as np, math, os, subprocess
from app.video.assemble import audio_duration_sec

def ken_burns_clip(images, out_path:str, audio_file:str, fps=25, size=(960,540)):
    """
    Simple pan/zoom montage from a list of image paths.
    - images: list of image file paths
    - out_path: output video path
    """
    w, h = size
    total_frames = int(audio_duration_sec(audio_file) * fps)
    if not images:
        raise ValueError("No images provided for montage.")
    # Equal segment per image
    seg_frames = max(1, total_frames // len(images))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # will be recompressed later via ffmpeg
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    for idx, img_path in enumerate(images):
        img = cv2.imread(img_path)
        if img is None:
            # fallback: blank frame
            img = np.zeros((h,w,3), dtype=np.uint8)
        ih, iw = img.shape[:2]
        # We'll create a slight zoom-in and pan
        for f in range(seg_frames):
            t = f / max(1, seg_frames-1)
            # zoom from 1.05 -> 1.15
            zoom = 1.05 + 0.1 * t
            crop_w = int(iw / zoom)
            crop_h = int(ih / zoom)
            # pan from center slightly to right/down
            cx = int((iw - crop_w) * (0.5 + 0.1 * t))
            cy = int((ih - crop_h) * (0.5 + 0.1 * t))
            cx = max(0, min(cx, iw - crop_w))
            cy = max(0, min(cy, ih - crop_h))
            crop = img[cy:cy+crop_h, cx:cx+crop_w]
            frame = cv2.resize(crop, (w, h), interpolation=cv2.INTER_CUBIC)
            writer.write(frame)

    # pad last frame if needed
    written = seg_frames * len(images)
    for _ in range(max(0, total_frames - written)):
        writer.write(frame)

    out_path_audio = out_path.strip().split(".mp4")[0]+"_audio.mp4"   
    writer.release()
    cmd = ["ffmpeg", "-i", out_path, "-i", audio_file, "-c:v", "copy", "-c:a", "aac", "-shortest", out_path_audio]
    subprocess.run(cmd, check=True)
    os.remove(out_path)
    os.rename(out_path_audio, out_path)   
    return out_path
