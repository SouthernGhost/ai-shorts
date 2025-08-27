import json, os, pathlib

def load_spec(path):
    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    return spec

def ensure_dir(p):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def which(cmd):
    from shutil import which
    return which(cmd)
