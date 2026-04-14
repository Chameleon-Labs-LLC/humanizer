"""Humanizer — update the agent config.

Run this to bump the agent to a new version after editing `writing_guardrails.md`
or changing the tool list. Existing sessions keep their pinned version; new
sessions (created via `run.py`) pick up the latest unless you pin explicitly.
"""
from __future__ import annotations

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from setup import build_system_prompt

load_dotenv()

HERE = Path(__file__).parent
GUARDRAILS_PATH = HERE / "writing_guardrails.md"


def main() -> None:
    client = anthropic.Anthropic()
    agent_id = os.environ["HUMANIZER_AGENT_ID"]

    guardrails = GUARDRAILS_PATH.read_text()
    system_prompt = build_system_prompt(guardrails)

    updated = client.beta.agents.update(
        agent_id=agent_id,
        system=system_prompt,
    )
    print(f"agent_id:      {updated.id}")
    print(f"agent_version: {updated.version}  (new)")
    print("\nNew sessions (string-shorthand agent reference) pick this up automatically.")
    print("To pin existing callers to the old version, replace the bare ID with:")
    print('  agent={"type": "agent", "id": AGENT_ID, "version": OLD_VERSION}')


if __name__ == "__main__":
    main()
