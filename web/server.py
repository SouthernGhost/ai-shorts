from flask import Flask, request, render_template, jsonify
import os, uuid, pathlib, subprocess, sys

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    if "spec" not in request.files:
        return "Upload a spec.json", 400
    job_id = str(uuid.uuid4())[:8]
    workdir = pathlib.Path(f"runs/{job_id}")
    workdir.mkdir(parents=True, exist_ok=True)
    spec_fp = workdir/"spec.json"
    request.files["spec"].save(spec_fp)

    out_mp4 = workdir/"out.mp4"
    # Fire-and-forget (no progress piping in this minimal version)
    python_executable = sys.executable
    subprocess.Popen([python_executable, "generate.py", "--spec", str(spec_fp), "--out", str(out_mp4), "--workdir", str(workdir)])

    return jsonify({"job_id": job_id, "out": str(out_mp4)})

@app.route("/outputs/<job_id>", methods=["GET"])
def outputs(job_id):
    p = pathlib.Path("runs")/job_id
    if not p.exists(): return ("Not found", 404)
    items = [str(x) for x in p.glob("*")]
    return jsonify({"job_id": job_id, "files": items})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
