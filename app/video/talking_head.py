import os, shutil, subprocess

def generate_talking_head(portrait_path, audio_wav, out_mp4, engine="wav2lip"):
    """
    Stub that calls external tool if available.
    For Wav2Lip: set env WAV2LIP_PATH to repo folder containing inference scripts.
    For SadTalker: set env SADTALKER_PATH similarly.
    """
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)

    if engine.lower() == "wav2lip":
        repo = os.getenv("WAV2LIP_PATH", None)
        if repo and os.path.exists(repo):
            # Example call (this depends on your local Wav2Lip setup)
            # Adjust paths/flags to match your cloned repo.
            cmd = ["poetry", "run",
                "python", os.path.join(repo, "inference.py"),
                "--checkpoint_path", os.path.join(repo, "checkpoints", "Wav2Lip-SD-GAN.pt"),
                "--face", portrait_path,
                "--audio", audio_wav,
                "--outfile", out_mp4
            ]
            subprocess.run(cmd, check=True)
            return out_mp4
        else:
            raise RuntimeError("WAV2LIP_PATH not set or invalid. Install Wav2Lip and set environment variable.")
    elif engine.lower() == "sadtalker":
        repo = os.getenv("SADTALKER_PATH", None)
        if repo and os.path.exists(repo):
            # Example call (adjust to your local SadTalker CLI)
            cmd = ["poetry", "run",
                "python", os.path.join(repo, "inference.py"),
                "--source_image", portrait_path,
                "--driven_audio", audio_wav,
                "--result_dir", os.path.dirname(out_mp4),
                "--enhancer", "gfpgan"
            ]
            subprocess.run(cmd, check=True)
            # Find output mp4 under result_dir, move/rename to out_mp4
            # (Left as an exercise; projects output with different filenames.)
            return out_mp4
        else:
            raise RuntimeError("SADTALKER_PATH not set or invalid. Install SadTalker and set environment variable.")
    else:
        raise ValueError(f"Unknown talking head engine: {engine}")
