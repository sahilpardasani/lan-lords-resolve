#!/usr/bin/env python3
"""Lightweight, non-destructive tests for the frozen Coder 1 runtime."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runtime import doctor


class RuntimeTests(unittest.TestCase):
    def test_wrong_model_fails_safely(self):
        payload = json.dumps({"model":"definitely-not-installed","messages":[{"role":"user","content":"test"}],"max_tokens":1}).encode()
        request = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", data=payload, headers={"Content-Type":"application/json"})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=10)
        self.assertIn(caught.exception.code, (400, 404))

    def test_unavailable_model_has_no_network_fallback(self):
        ok, detail = doctor.http_json("http://127.0.0.1:9/v1/models", timeout=1)
        self.assertFalse(ok)
        self.assertTrue(detail)

    def test_mongo_unavailable_diagnostic(self):
        self.assertFalse(doctor.tcp_open("127.0.0.1", 9, timeout=0.1))

    def test_openshell_public_http_is_policy_blocked(self):
        rc, output = doctor.command(str(doctor.OPEN_SHELL), "sandbox", "exec", "-n", "resolve-containment", "--no-tty", "--", "curl", "--fail", "--silent", "--show-error", "http://example.com/", timeout=20)
        self.assertNotEqual(rc, 0, output)
        self.assertTrue("403" in output or "not permitted by policy" in output, output)

    def test_openshell_local_model_allowed(self):
        rc, output = doctor.command(str(doctor.OPEN_SHELL), "sandbox", "exec", "-n", "resolve-containment", "--no-tty", "--", "curl", "--fail", "--silent", "--show-error", "http://host.openshell.internal:8000/v1/models", timeout=20)
        self.assertEqual(rc, 0, output)
        self.assertIn(doctor.MODEL_ALIAS, output)

    def test_live_model_route(self):
        ok, body = doctor.http_json("http://127.0.0.1:8000/v1/models")
        self.assertTrue(ok, body)
        self.assertIn(doctor.MODEL_ALIAS, [x["id"] for x in body["data"]])

    def test_live_mongo_ping(self):
        rc, output = doctor.command("docker", "exec", "resolve-mongodb", "mongosh", "--quiet", "--eval", "db.runCommand({ping:1})")
        self.assertEqual(rc, 0, output)
        self.assertIn("ok: 1", output)

    def test_model_mount_read_only(self):
        info = doctor.container("resolve-vllm")
        self.assertIsNotNone(info)
        self.assertTrue(any(m["Destination"] == "/model" and not m["RW"] for m in info["Mounts"]))

    def test_vllm_digest(self):
        info = doctor.container("resolve-vllm")
        self.assertEqual(info["Config"]["Image"], f"nvcr.io/nvidia/vllm@{doctor.VLLM_DIGEST}")

    def test_mongo_digest(self):
        info = doctor.container("resolve-mongodb")
        self.assertEqual(info["Config"]["Image"], f"mongo@{doctor.MONGO_DIGEST}")

    def test_openshell_binary_and_version(self):
        self.assertEqual(str(doctor.OPEN_SHELL), "/usr/bin/openshell")
        rc, output = doctor.command(str(doctor.OPEN_SHELL), "--version")
        self.assertEqual((rc, output), (0, doctor.EXPECTED_OPEN_SHELL))

    def test_missing_artifacts_fail_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            ok, detail = doctor.model_artifacts(Path(directory))
        self.assertFalse(ok)
        self.assertIn("model.safetensors", detail)

    def test_no_stale_mac_paths(self):
        result = subprocess.run(["rg", "-n", "/" + "Volumes/Elements|/" + "Users/", ".", "-g", "!.git/**"], cwd=ROOT, text=True, stdout=subprocess.PIPE)
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_no_tracked_weights(self):
        files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        bad = [x for x in files if x.endswith((".safetensors", ".gguf", ".bin"))]
        self.assertEqual(bad, [])

    def test_no_tracked_env_or_private_key(self):
        files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        bad = [x for x in files if Path(x).name.startswith(".env") or Path(x).suffix in (".pem", ".key")]
        self.assertEqual(bad, [])

    def test_no_secret_material_in_tracked_content(self):
        files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        expressions = (
            re.compile("BEGIN " + r"(?:RSA |OPENSSH |EC )?PRIVATE KEY"),
            re.compile("gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
            re.compile("hf" + r"_[A-Za-z0-9]{20,}"),
        )
        findings = []
        for name in files:
            try:
                raw = (ROOT / name).read_bytes()
            except OSError:
                continue
            if b"\0" in raw:
                continue
            text = raw.decode(errors="ignore")
            if any(expression.search(text) for expression in expressions):
                findings.append(name)
        self.assertEqual(findings, [])

    def test_openshell_gateway_not_wildcard_bound(self):
        rc, output = doctor.command("ss", "-ltn")
        self.assertEqual(rc, 0, output)
        gateway_lines = [line for line in output.splitlines() if ":17670" in line]
        self.assertTrue(gateway_lines, output)
        self.assertFalse(any("0.0.0.0:17670" in line or "[::]:17670" in line or "*:17670" in line for line in gateway_lines), gateway_lines)

    def test_offline_flags(self):
        info = doctor.container("resolve-vllm")
        env = set(info["Config"]["Env"])
        self.assertTrue({"HF_HUB_OFFLINE=1", "TRANSFORMERS_OFFLINE=1"}.issubset(env))

    def test_tool_fixture_cannot_execute_shell(self):
        source = (ROOT / "runtime/model_acceptance.py").read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)
        self.assertIn('assert fact_id == "FACT-742"', source)

    def test_ports_have_no_wildcard_publication(self):
        for name in ("resolve-vllm", "resolve-mongodb"):
            info = doctor.container(name)
            for bindings in info["HostConfig"]["PortBindings"].values():
                for binding in bindings:
                    self.assertNotIn(binding["HostIp"], ("", "0.0.0.0", "::"))

    def test_recovery_is_documented(self):
        text = (ROOT / "docs/C1_OPERATIONS.md").read_text()
        self.assertIn("## Recover", text)
        self.assertIn("--enforce-eager", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
