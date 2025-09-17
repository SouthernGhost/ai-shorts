import os
import sys
import subprocess
import pathlib


def face_swap(portrait: str, target: str):
    # Get the project root directory (where generate.py is located)
    project_root = pathlib.Path(__file__).parent.parent.parent.absolute()
    
    # Resolve relative paths to absolute paths
    portrait_abs = str(project_root / portrait)
    target_abs = str(project_root / target)
    
    if not os.path.isfile(portrait_abs):
        raise RuntimeError(f"Invalid path to portrait file: {portrait_abs}. Make sure path is correct and the file exists.")
    if not os.path.isfile(target_abs):
        raise RuntimeError(f"Invalid path to target file: {target_abs}. Make sure path is correct and the file exists.")

    # Create output filename from portrait filename only (not full path)
    portrait_name = pathlib.Path(portrait).stem
    output_path = str(project_root / f"examples/face_swaps/{portrait_name}_swap.jpg")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    repo = os.getenv('FACEFUSION_PATH')
    cmd = [sys.executable,
                "facefusion.py",
                "headless-run",
                "--config-path", os.path.join(repo, "facefusion.ini"),
                "--jobs-path", os.path.join(repo, ".jobs"),
                "--processors", "face_swapper", "face_enhancer",
                "--face-swapper-model", "inswapper_128_fp16",
                "--face-swapper-weight", "0.3",
                "--face-enhancer-model", "gfpgan_1.4",
                "-s", portrait_abs,  # Use absolute path
                "-t", target_abs,    # Use absolute path
                "--output-path", output_path]
    try:
        cwd = str(project_root / "third_party/facefusion")
        subprocess.run(cmd, cwd=cwd)
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    return output_path