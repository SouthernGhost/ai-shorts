import os, shutil, subprocess

def generate_talking_head(portrait_path, audio_wav, out_mp4, engine="wav2lip", target_width=960, target_height=540):
    """
    Generate talking head with standardized output resolution to prevent stretching.
    """
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)

    if engine.lower() == "wav2lip":
        repo = os.getenv("WAV2LIP_PATH", None)
        if repo and os.path.exists(repo):
            # Generate raw output first
            raw_output = out_mp4.replace('.mp4', '_raw.mp4')
            
            # Example call (this depends on your local Wav2Lip setup)
            # Adjust paths/flags to match your cloned repo.
            cmd = ["poetry", "run",
                "python", os.path.join(repo, "inference.py"),
                "--checkpoint_path", os.path.join(repo, "checkpoints", "Wav2Lip-SD-GAN.pt"),
                "--face", portrait_path,
                "--audio", audio_wav,
                "--outfile", raw_output
            ]
            subprocess.run(cmd, check=True)
            
            # Post-process to standardize resolution and prevent stretching
            subprocess.run([
                "ffmpeg", "-y", "-i", raw_output,
                "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height}",
                "-c:v", "libx264", "-c:a", "aac",
                out_mp4
            ], check=True)
            
            # Clean up raw output
            if os.path.exists(raw_output):
                os.remove(raw_output)
            return out_mp4
        else:
            raise RuntimeError("WAV2LIP_PATH not set or invalid. Install Wav2Lip and set environment variable.")
    elif engine.lower() == "sadtalker":
        repo = os.getenv("SADTALKER_PATH", None)
        if repo and os.path.exists(repo):
            # Generate raw output first
            raw_output = out_mp4.replace('.mp4', '_raw.mp4')
            
            # Example call (adjust to your local SadTalker CLI)
            cmd = ["poetry", "run",
                "python", os.path.join(repo, "inference.py"),
                "--source_image", portrait_path,
                "--driven_audio", audio_wav,
                "--checkpoint_dir", "SadTalker/checkpoints/",
                "--bfm_folder", "SadTalker/checkpoints/BFM_Fitting",
                "--result_dir", os.path.dirname(out_mp4),
                "--enhancer", "gfpgan",
                "--still",
                "--preprocess", "full",
                "--expression_scale", "0.8"
            ]
            subprocess.run(cmd, check=True)
            
            # Find output mp4 under result_dir, move/rename to raw_output
            # (This part needs to be adapted based on SadTalker's actual output naming)
            # For now, assuming it outputs to the result_dir with a predictable name
            result_files = [f for f in os.listdir(os.path.dirname(out_mp4)) if f.endswith('.mp4')]
            if result_files:
                temp_result = os.path.join(os.path.dirname(out_mp4), result_files[0])
                if temp_result != raw_output:
                    os.rename(temp_result, raw_output)
            
            # Post-process to standardize resolution
            if os.path.exists(raw_output):
                subprocess.run([
                    "ffmpeg", "-y", "-i", raw_output,
                    "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height}",
                    "-c:v", "libx264", "-c:a", "aac",
                    out_mp4
                ], check=True)
                
                # Clean up raw output
                os.remove(raw_output)
            
            return out_mp4
        else:
            raise RuntimeError("SADTALKER_PATH not set or invalid. Install SadTalker and set environment variable.")
    else:
        raise ValueError(f"Unknown talking head engine: {engine}")
