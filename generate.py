import argparse, pathlib, os
from app.pipeline import run_project
from app.utils.io import ensure_dir

print(os.environ['PIPER_VOICE'])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path to spec JSON")
    ap.add_argument("--out", required=True, help="Output MP4 path")
    ap.add_argument("--workdir", default="runs/_latest", help="Working directory for intermediates")
    args = ap.parse_args()

    ensure_dir(pathlib.Path(args.out).parent)
    ensure_dir(args.workdir)
    run_project(args.spec, args.out, args.workdir)

if __name__ == "__main__":
    main()
