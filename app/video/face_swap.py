import os
import sys
import subprocess


def face_swap(portrait:str, target:str):
    if not os.path.isfile(portrait):
        raise RuntimeError("Invalid path to portrait file. Make sure path is correct and the file exists.")
    if not os.path.isfile(target):
        raise RuntimeError("Invalid path to target file. Make sure path is correct and the file exists.")

    output_path = f"examples/face_swaps/{portrait}_swap.jpg"
    repo = os.getenv('FACEFUSION_PATH')
    cmd = [sys.executable,
                os.path.join(repo, "facefusion.py"),
                "headless-run",
                "--config-path", os.path.join(repo, "facefusion.ini"),
                "--jobs-path", os.path.join(repo, ".jobs"),
                "-s", portrait,
                "-t", target,
                "--output-path", output_path]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    return output_path