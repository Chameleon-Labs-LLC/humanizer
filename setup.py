"""Humanizer — one-time setup.

Creates the Managed Agent and Environment on the Anthropic Claude API.
Run this ONCE. Save the printed IDs to your .env file.

Re-run only when you want to rebuild from scratch. To modify the agent's
system prompt or tools later, use `update.py` instead (it bumps the
version without losing session history on the previous one).
"""
from __future__ import annotations

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

HERE = Path(__file__).parent
GUARDRAILS_PATH = HERE / "writing_guardrails.md"


def build_system_prompt(guardrails: str) -> str:
    return f"""You are Humanizer, a writing agent that eliminates AI fingerprints and replaces them with a user's personal voice.

On EVERY writing task:
1. Call `get_user_dna` FIRST to fetch the current user's Text DNA Bible.
2. Apply the Writing Guardrails below (negative rules, never violate).
3. Apply the user's Text DNA Bible (positive rules, match their voice).
4. Never mention these rules, the tool call, or that you are an AI following guidelines. Just write.

When the user asks you to rewrite a document, use the file tools to operate on it directly. Read the input, produce the rewritten version, and write it to the location the user specified (or `/mnt/session/outputs/` if they did not specify).

---

{guardrails}
"""


def main() -> None:
    client = anthropic.Anthropic()

    guardrails = GUARDRAILS_PATH.read_text()
    system_prompt = build_system_prompt(guardrails)

    print("Creating environment...")
    environment = client.beta.environments.create(
        name=os.environ.get("HUMANIZER_ENV_NAME", "humanizer-env"),
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"  environment_id: {environment.id}")

    print("Creating agent...")
    agent = client.beta.agents.create(
        name="Humanizer",
        description="Strips AI fingerprints from writing and replaces with user's voice",
        model="claude-opus-4-6",
        system=system_prompt,
        tools=[
            # File ops only — no bash, no web. This agent just reads and rewrites text.
            {
                "type": "agent_toolset_20260401",
                "default_config": {"enabled": False},
                "configs": [
                    {"name": "read", "enabled": True},
                    {"name": "write", "enabled": True},
                    {"name": "edit", "enabled": True},
                    {"name": "glob", "enabled": True},
                    {"name": "grep", "enabled": True},
                ],
            },
            # Custom tool: host app fetches per-user DNA Bible and returns it to the agent.
            {
                "type": "custom",
                "name": "get_user_dna",
                "description": (
                    "Fetch the current user's Text DNA Bible — their personal voice profile "
                    "covering rhythm, vocabulary, humor, formatting, and content philosophy. "
                    "Call this at the start of every writing task before producing any output."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ],
    )
    print(f"  agent_id:      {agent.id}")
    print(f"  agent_version: {agent.version}")

    print("\nAdd these to your .env file:")
    print(f"HUMANIZER_ENV_ID={environment.id}")
    print(f"HUMANIZER_AGENT_ID={agent.id}")
    print(f"HUMANIZER_AGENT_VERSION={agent.version}")


if __name__ == "__main__":
    main()
