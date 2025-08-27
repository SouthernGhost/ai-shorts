# AI Shorts (Local, macOS-friendly)

**MVP features**: JSON spec -> local TTS -> narration montage (Ken Burns) or *stub* talking-head (Wav2Lip/SadTalker) -> subtitles/watermark -> compression (2–5 MB).

## Quick start (macOS)
```bash
cd ai_shorts
bash scripts/setup_macos.sh
# Activate venv
source .venv/bin/activate

# (Optional) Install/prepare TTS:
# - Piper: install 'piper' binary, download a voice model (e.g., en_US-amy-low.onnx), set env PIPER_VOICE or put voice path in spec.
# macOS fallback uses 'say' if Piper isn't set.

# Generate from sample spec (will only fully work for narration scene s1)
python generate.py --spec examples/spec_sample.json --out runs/demo/out.mp4 --workdir runs/demo
```

### Talking-head note
Wav2Lip/SadTalker require cloning their repos and models. Then set env:
```
export WAV2LIP_PATH=/path/to/Wav2Lip
# or
export SADTALKER_PATH=/path/to/SadTalker
```
Scene `s2` in the sample spec will error until one of these is installed.

## Flask UI
```bash
export FLASK_APP=web/server.py
python web/server.py
# open http://127.0.0.1:5000
```

## Spec format
See `examples/spec_sample.json`. Provide per-scene `mode: "narration"` or `"talking_head"`.

## Compression targets
The pipeline uses ffmpeg 2-pass to aim for 2–5 MB at 15–30s with 540p @ 25 fps.
Adjust `target_size_mb` in the spec.

## Notes
- Keep everything local. No cloud calls.
- Add watermark and avoid voice cloning of real people without consent.
- For better voice quality, integrate Coqui TTS instead of Piper/macOS 'say'.


## Windows Setup (CPU or NVIDIA GPU)

### Option A: venv (PowerShell)
```powershell
# from project root
.\scripts\setup_windows.ps1           # CPU setup
# or with CUDA-enabled PyTorch (requires NVIDIA GPU + drivers)
.\scripts\setup_windows.ps1 -Cuda

# activate
.\.venv\Scripts\activate
```

### Option B: Batch wrapper (cmd.exe)
```bat
scripts\setup_windows.bat         
scripts\setup_windows.bat cuda    REM for CUDA PyTorch
```

### ffmpeg
Install and add to PATH. Easiest via Chocolatey:
```powershell
choco install ffmpeg
```

### Piper TTS
Download a voice and set env var:
```powershell
# download (defaults to en_US-amy-low)
.\.venv\Scripts\python scripts\download_piper_voice.py
# set env so tts.py can find it
setx PIPER_VOICE "%CD%\models\piper\en_US-amy-low.onnx"
```

### (Optional) Wav2Lip / SadTalker
Clone the repos and place checkpoints, then set env:
```powershell
setx WAV2LIP_PATH "C:\path\to\Wav2Lip"
REM or
setx SADTALKER_PATH "C:\path\to\SadTalker"
```

### Run generation
```powershell
.\.venv\Scripts\activate
python generate.py --spec examples\spec_sample.json --out runs\demo\out.mp4 --workdir runs\demo
```

### Flask UI
```powershell
python web\server.py
# open http://127.0.0.1:5000
```
