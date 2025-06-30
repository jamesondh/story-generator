#!/usr/bin/env python3
"""
Sequentially drives the LLM through REFINE → GENERATE → CRITIQUE.

Usage:  python generate_variations.py <STAGE>
"""
import subprocess, sys, json, textwrap
STAGE = sys.argv[1]

def call_llm(role, payload):
    """Thin wrapper over your preferred LLM CLI (claude‑code, gpt‑cli, etc.)."""
    cmd = ["llm", "--role", role, "--json", json.dumps(payload)]
    return subprocess.check_output(cmd, text=True)

# 1) REFINE  ────────────────────────────────────────────────────────────
qs = call_llm("system", {"task": "ask_refinement", "stage": STAGE})
print(textwrap.dedent(qs))
answers = input("\nYour answers (JSON or multiline):\n")  # simple CLI

# 2) GENERATE
gen_payload = {"task": "generate_variations", "stage": STAGE, "answers": answers}
print("⏳  Generating variations…")
_ = call_llm("system", gen_payload)

# 3) CRITIQUE
crit = call_llm("system", {"task": "critique_last_variations", "stage": STAGE})
print(crit)

print("\nDone. Review critique & run APPLY when ready.")