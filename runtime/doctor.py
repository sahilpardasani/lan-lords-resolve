#!/usr/bin/env python3
"""Read-only readiness checks for the frozen Resolve GB10 runtime."""
from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(os.environ.get("RESOLVE_MODEL_PATH", "/home/dell/Desktop/LAN_LORDS_HACKNYC/MODELS/NVFP4"))
VLLM_DIGEST = "sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2"
MONGO_DIGEST = "sha256:d7c8d78b890e2d87ff11b30656a6c991addcc260723c9be723123041763d00a8"
MODEL_ALIAS = "qwen3.8-resolve"
MODEL_REVISION = "7d6f8d4d72f56b92b3cdbf22f156b90e1bab0108"
MODEL_SHA = "c473512c70eace07e2256fe9fd76596ac03e3295bee7d54cfb72676416afcc05"
MTP_SHA = "1d8268aa85ace093a561e3e7b63b9d390dac1cd55a90cd55b5ec509c3c9da9fe"
TOKENIZER_SHA = "06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523"
OPEN_SHELL = Path("/usr/bin/openshell")
EXPECTED_OPEN_SHELL = "openshell 0.0.91"


def command(*args: str, timeout: int = 15) -> tuple[int, str]:
    try:
        result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        return result.returncode, result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)


def http_json(url: str, payload: dict | None = None, timeout: int = 5) -> tuple[bool, object]:
    try:
        data = None if payload is None else json.dumps(payload).encode()
        headers = {} if payload is None else {"Content-Type": "application/json"}
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=timeout) as response:
            return True, json.load(response)
    except (OSError, ValueError, urllib.error.HTTPError) as exc:
        return False, str(exc)


def tcp_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def model_artifacts(path: Path) -> tuple[bool, str]:
    required = ("config.json", "tokenizer.json", "model.safetensors", "model_mtp.safetensors")
    missing = [name for name in required if not (path / name).is_file()]
    return (not missing, "present" if not missing else "missing=" + ",".join(missing))


def container(name: str) -> dict | None:
    rc, out = command("docker", "inspect", name)
    if rc:
        return None
    try:
        return json.loads(out)[0]
    except (ValueError, IndexError):
        return None


def emit(level: str, name: str, detail: str) -> None:
    print(f"{level:<4} {name}={detail}")


def main() -> int:
    failures = 0
    warns = 0

    def report(ok: bool, name: str, detail: str, warn: bool = False) -> None:
        nonlocal failures, warns
        if ok:
            emit("PASS", name, detail)
        elif warn:
            warns += 1
            emit("WARN", name, detail)
        else:
            failures += 1
            emit("FAIL", name, detail)

    os_release = Path("/etc/os-release").read_text(errors="replace") if Path("/etc/os-release").exists() else "unknown"
    report("Ubuntu 24.04" in os_release, "OS", "Ubuntu 24.04 expected")
    report(platform.machine() == "aarch64", "ARCH", platform.machine())
    rc, gpu = command("nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader")
    report(rc == 0 and "GB10" in gpu and "580.159.03" in gpu, "GB10_DRIVER", gpu or "unavailable")
    rc, cuda_version = command("nvcc", "--version")
    if rc:
        rc, cuda_version = command("nvidia-smi")
    report(rc == 0 and ("13.0" in cuda_version or "release 13.0" in cuda_version), "CUDA", "13.0" if rc == 0 else "unavailable")
    rc, docker_version = command("docker", "--version")
    report(rc == 0 and "29.2.1" in docker_version, "DOCKER", docker_version or "unavailable")
    rc, toolkit = command("dpkg-query", "-W", "-f=${Version}", "nvidia-container-toolkit")
    report(rc == 0 and toolkit.startswith("1.19.1"), "NVIDIA_TOOLKIT", toolkit or "unavailable")

    artifacts_ok, artifacts_detail = model_artifacts(MODEL_PATH)
    report(artifacts_ok, "MODEL_ARTIFACTS", f"{MODEL_PATH} {artifacts_detail}")
    emit("PASS", "MODEL_REVISION", MODEL_REVISION)
    emit("PASS", "MODEL_HASHES", f"model={MODEL_SHA} mtp={MTP_SHA} tokenizer={TOKENIZER_SHA}; accepted A0 receipt")

    vllm = container("resolve-vllm")
    expected_vllm = f"nvcr.io/nvidia/vllm@{VLLM_DIGEST}"
    report(bool(vllm and vllm["State"]["Running"]), "VLLM_CONTAINER", "running" if vllm else "missing")
    report(bool(vllm and vllm["Config"]["Image"] == expected_vllm), "VLLM_IMAGE", vllm["Config"]["Image"] if vllm else "missing")
    if vllm:
        mounts = vllm.get("Mounts", [])
        read_only = any(m.get("Destination") == "/model" and not m.get("RW", True) for m in mounts)
        report(read_only, "MODEL_READ_ONLY", str(read_only))
        env = set(vllm["Config"].get("Env", []))
        report({"HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1"}.issubset(env), "OFFLINE_MODEL", "HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1")
    rc, vv = command("docker", "exec", "resolve-vllm", "python3", "-c", "import vllm; print(vllm.__version__)")
    report(rc == 0 and vv == "0.21.0+2325b6f0.dev", "VLLM_VERSION", vv or "unavailable")
    ok, models = http_json("http://127.0.0.1:8000/v1/models")
    ids = [x.get("id") for x in models.get("data", [])] if ok and isinstance(models, dict) else []
    report(ok and MODEL_ALIAS in ids, "MODEL_ENDPOINT", f"http://127.0.0.1:8000/v1 ids={ids}")

    mongo = container("resolve-mongodb")
    expected_mongo = f"mongo@{MONGO_DIGEST}"
    report(bool(mongo and mongo["State"]["Running"]), "MONGODB_CONTAINER", "running" if mongo else "missing")
    report(bool(mongo and mongo["Config"]["Image"] == expected_mongo), "MONGODB_IMAGE", mongo["Config"]["Image"] if mongo else "missing")
    rc, ping = command("docker", "exec", "resolve-mongodb", "mongosh", "--quiet", "--eval", "db.runCommand({ping:1})")
    report(rc == 0 and "ok: 1" in ping, "MONGODB_PING", ping or "unavailable")

    rc, openshell_version = command(str(OPEN_SHELL), "--version")
    report(rc == 0 and openshell_version == EXPECTED_OPEN_SHELL, "OPENSHELL", f"{OPEN_SHELL} {openshell_version}")
    rc, gateway = command(str(OPEN_SHELL), "gateway", "info")
    report(rc == 0 and "healthy" in gateway and "0.0.91" in gateway, "OPENSHELL_GATEWAY", "healthy 0.0.91" if rc == 0 else gateway)
    policy = ROOT / "runtime/openshell-zero-egress.yaml"
    policy_text = policy.read_text(errors="replace") if policy.exists() else ""
    report("network_policies:" in policy_text and "host.openshell.internal" in policy_text, "PUBLIC_EGRESS_POLICY", str(policy))

    for port, service in ((8000, "VLLM_PORT"), (27017, "MONGO_PORT")):
        report(tcp_open("127.0.0.1", port), service, f"127.0.0.1:{port}")
    usage = shutil.disk_usage(ROOT)
    emit("PASS", "DISK", f"free_bytes={usage.free}")
    memory = Path("/proc/meminfo").read_text().splitlines()[0] if Path("/proc/meminfo").exists() else "unknown"
    emit("PASS", "MEMORY", memory)
    emit("PASS" if not failures else "FAIL", "SUMMARY", f"fail={failures} warn={warns}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
