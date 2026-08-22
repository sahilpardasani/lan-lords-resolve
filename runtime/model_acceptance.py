#!/usr/bin/env python3
"""Local-only acceptance checks for the frozen Resolve model endpoint."""

import json
import sys
import urllib.request
from pathlib import Path


BASE = "http://127.0.0.1:8000"
MODEL = "qwen3.8-resolve"
OUT = Path("evidence/model_acceptance")


def post(path: str, payload: dict, timeout: int = 600) -> dict:
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def chat(messages: list[dict], **extra: object) -> dict:
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "stream": False,
        "max_tokens": 256,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    payload.update(extra)
    return post("/v1/chat/completions", payload)


DECISION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "resolve_decision",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "decision": {"type": "string", "enum": ["BLOCK", "ALLOW"]},
                "reason_code": {"type": "string"},
                "action": {"type": "string"},
            },
            "required": ["decision", "reason_code", "action"],
            "additionalProperties": False,
        },
    },
}


def structured() -> None:
    prompt = (
        "Policy: Processor B may receive at most 20% of total traffic. "
        "Proposal: route 100% of traffic to Processor B. Return the structured "
        "decision. Use reason_code TRAFFIC_CAP and action KEEP_CURRENT_ROUTING."
    )
    runs = []
    material = []
    for _ in range(3):
        response = chat([{"role": "user", "content": prompt}], response_format=DECISION_SCHEMA)
        parsed = json.loads(response["choices"][0]["message"]["content"])
        assert parsed["decision"] == "BLOCK"
        assert parsed["reason_code"] == "TRAFFIC_CAP"
        assert parsed["action"] == "KEEP_CURRENT_ROUTING"
        runs.append({"response": response, "parsed": parsed})
        material.append(parsed)
    assert all(item == material[0] for item in material)
    (OUT / "structured_response.json").write_text(json.dumps({"runs": runs}, indent=2) + "\n")
    print("A2B=PASS")
    print("A3=PASS")


TOOL = {
    "type": "function",
    "function": {
        "name": "lookup_test_fact",
        "description": "Look up a local acceptance-test fact by identifier.",
        "parameters": {
            "type": "object",
            "properties": {"fact_id": {"type": "string"}},
            "required": ["fact_id"],
            "additionalProperties": False,
        },
    },
}


def lookup_test_fact(fact_id: str) -> dict:
    assert fact_id == "FACT-742"
    return {"fact_id": fact_id, "value": "CURRENT_AND_VERIFIED"}


def one_tool(prompt: str) -> dict:
    messages = [{"role": "user", "content": prompt}]
    first = chat(messages, tools=[TOOL], tool_choice="auto")
    assistant = first["choices"][0]["message"]
    calls = assistant.get("tool_calls") or []
    assert calls, "no actual tool_calls event"
    call = calls[0]
    assert call["function"]["name"] == "lookup_test_fact"
    arguments = json.loads(call["function"]["arguments"])
    result = lookup_test_fact(arguments["fact_id"])
    messages.extend(
        [
            assistant,
            {
                "role": "tool",
                "tool_call_id": call["id"],
                "name": "lookup_test_fact",
                "content": json.dumps(result),
            },
        ]
    )
    final = chat(messages, tools=[TOOL], tool_choice="auto")
    content = final["choices"][0]["message"]["content"] or ""
    assert "CURRENT_AND_VERIFIED" in content
    return {"initial_response": first, "local_tool_result": result, "final_response": final}


def tools() -> None:
    prompt = "Use lookup_test_fact to retrieve FACT-742, then report its value."
    for index in range(1, 4):
        transcript = one_tool(prompt)
        (OUT / f"tool_call_{index}.json").write_text(json.dumps(transcript, indent=2) + "\n")
    print("A4=PASS")


def long_context(require_tool: bool) -> None:
    prefix = "Synthetic audit evidence line: no applicable processor fact appears here.\n"
    evidence = prefix * 1000
    evidence += "FACT-742: backup_processor_capacity_status=CURRENT_AND_VERIFIED\n"
    evidence += prefix * 300
    if require_tool:
        prompt = (
            evidence
            + "\nFind the fact identifier relevant to backup_processor_capacity_status, "
            "call lookup_test_fact with it, and report the tool's value."
        )
        transcript = one_tool(prompt)
        target = OUT / "long_context_tool_result.json"
        target.write_text(json.dumps(transcript, indent=2) + "\n")
        print("A6=PASS")
    else:
        response = chat(
            [{"role": "user", "content": evidence + "\nWhat is backup_processor_capacity_status for FACT-742? Reply with only its value."}],
            max_tokens=32,
        )
        content = response["choices"][0]["message"]["content"].strip()
        assert content == "CURRENT_AND_VERIFIED", repr(content)
        (OUT / "long_context_result.json").write_text(json.dumps(response, indent=2) + "\n")
        print("A5=PASS")


def challenger() -> None:
    prompt = """A payment processor is degraded.
Candidate action: route 100% of global payment traffic to Processor B.
Declared company policy:
- Processor B may receive at most 20% of TOTAL traffic
- Processor B may only receive eligible US Visa/Mastercard traffic
Identify why this exact proposed action should not proceed and identify the declared boundary/boundaries it violates."""
    response = post(
        "/v1/chat/completions",
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "stream": False,
            "max_tokens": 512,
            "chat_template_kwargs": {"enable_thinking": True},
        },
    )
    choice = response["choices"][0]
    assert choice.get("finish_reason") == "stop", f"truncated challenger: {choice.get('finish_reason')}"
    message = choice["message"]
    combined = ((message.get("reasoning") or "") + " " + (message.get("content") or "")).lower()
    assert "20%" in combined
    assert "100%" in combined
    assert "us" in combined
    assert "visa" in combined and "mastercard" in combined
    (OUT / "challenger_result.json").write_text(json.dumps(response, indent=2) + "\n")
    print("A7=PASS")


COMMANDS = {"structured": structured, "tools": tools, "long": lambda: long_context(False), "long-tool": lambda: long_context(True), "challenger": challenger}


if __name__ == "__main__":
    COMMANDS[sys.argv[1]]()
