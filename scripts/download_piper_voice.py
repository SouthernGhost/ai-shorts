import argparse, os, pathlib, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/amy/low/en_US-amy-low.onnx",
                    help="URL to Piper voice archive (.tar.gz or .onnx)")
    ap.add_argument("--outdir", default="models/piper", help="Directory to store voices")
    args = ap.parse_args()

    outdir = pathlib.Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    fn = outdir / os.path.basename(args.url)
    print(f"Downloading {args.url} -> {fn}")
    urllib.request.urlretrieve(args.url, fn)
    print("Downloaded.")
    if str(fn).endswith(".tar.gz"):
        import tarfile
        with tarfile.open(fn, "r:gz") as tar:
            tar.extractall(outdir)
        print(f"Extracted under {outdir}.")
    print("Remember to set PIPER_VOICE to the .onnx file path.")

if __name__ == "__main__":
    main()
