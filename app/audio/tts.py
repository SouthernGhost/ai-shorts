import subprocess, os, tempfile, shutil, sys, platform

def synthesize(text:str, out_wav:str, engine:str="piper", voice:str=None):
    """
    Generate speech audio to out_wav.
    Priority:
      - Piper (needs 'piper' binary and a voice model via PIPER_VOICE or `voice` path)
      - macOS 'say' fallback if available
    """
    os.makedirs(os.path.dirname(out_wav), exist_ok=True)
    text = text or ""

    if engine.lower() == "piper":
        piper_bin = shutil.which("piper")
        model = voice or os.getenv("PIPER_VOICE")  # e.g., en_US-amy-low.onnx
        if piper_bin and model and os.path.exists(model):
            cmd = [piper_bin, "-m", model, "--output_file", out_wav]
            # Piper expects text on stdin
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
                return out_wav
            except subprocess.CalledProcessError as e:
                print(f"[TTS] Piper failed: {e}. Falling back if possible.", file=sys.stderr)
        else:
            print("[TTS] Piper not configured (need 'piper' in PATH and voice model).", file=sys.stderr)

    if engine.lower() == 'bark':
        bark_bin = 'bark'
        env = os.environ.copy()
        env['SUNO_OFFLOAD_CPU'] = "True"
        env['SUNO_USE_SMALL_MODELS'] = "True"

        if bark_bin:
            cmd = [
                "poetry", "run", "python", "-m", bark_bin,
                "--text", text,
                "--output_filename", out_wav
            ]
            try:
                subprocess.run(cmd, input=text.encode("utf-8"), check=True, env=env)
                return out_wav
            except subprocess.CalledProcessError as e:
                print(f"[TTS] Bark failed: {e}. Falling back if possible.", file=sys.stderr)
        else:
            print(f"[TTS] Bark not configured or installed.")

    # Fallback for macOS: 'say' -> AIFF then ffmpeg to WAV
    if platform.system() == "Darwin" and shutil.which("say"):
        with tempfile.TemporaryDirectory() as td:
            aiff = os.path.join(td, "out.aiff")
            voice_flag = []
            if voice:
                # macOS voices differ from Piper voices; ignore if unknown
                voice_flag = ["-v", voice]
            try:
                subprocess.run(["say", *voice_flag, "-o", aiff, text], check=True)
                if shutil.which("ffmpeg"):
                    subprocess.run(["ffmpeg", "-y", "-i", aiff, "-ar", "16000", "-ac", "1", out_wav], check=True)
                else:
                    # On macOS, afconvert may exist
                    if shutil.which("afconvert"):
                        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", aiff, out_wav], check=True)
                    else:
                        raise RuntimeError("Neither ffmpeg nor afconvert available for conversion.")
                return out_wav
            except Exception as e:
                print(f"[TTS] macOS say fallback failed: {e}", file=sys.stderr)

    raise RuntimeError("No TTS path available. Install Piper + voice model or use macOS 'say'.")
