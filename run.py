"""Humanizer — runtime.

Opens a Managed Agent session, streams events, and handles the per-user DNA
custom tool call. Call `humanize()` once per user request.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

HERE = Path(__file__).parent
DNA_DIR = HERE / "user_dna"  # Stub store: one file per user_id. Replace with your DB in prod.


def fetch_user_dna(user_id: str) -> str:
    """Load the user's Text DNA Bible.

    This is the stub implementation — it reads from `user_dna/<user_id>.md` on disk.
    In production, replace with a database lookup (e.g. Prisma/Postgres, DynamoDB).
    """
    path = DNA_DIR / f"{user_id}.md"
    if not path.exists():
        # Fall back to the template's starter defaults so the agent still has a voice profile.
        return (HERE / "dna_bible_template.md").read_text()
    return path.read_text()


def humanize(
    user_id: str,
    prompt: str,
    document_path: Optional[str] = None,
    output_dir: str = "./outputs",
) -> None:
    """Run one Humanizer session.

    Args:
        user_id: Identifier used to look up the user's DNA Bible.
        prompt: The writing instruction (e.g. "rewrite /workspace/input.md").
        document_path: Optional local file to upload as a session resource.
        output_dir: Where to save any files the agent writes to /mnt/session/outputs/.
    """
    client = anthropic.Anthropic()

    env_id = os.environ["HUMANIZER_ENV_ID"]
    agent_id = os.environ["HUMANIZER_AGENT_ID"]

    # Upload the input document if provided, then mount it into the session.
    resources = []
    if document_path:
        ext = Path(document_path).suffix or ".txt"
        with open(document_path, "rb") as fh:
            uploaded = client.beta.files.upload(file=fh)
        resources.append(
            {
                "type": "file",
                "file_id": uploaded.id,
                "mount_path": f"/workspace/input{ext}",
            }
        )

    session = client.beta.sessions.create(
        agent=agent_id,  # string shorthand — uses agent's latest version
        environment_id=env_id,
        title=f"humanize-{user_id}",
        resources=resources,
    )
    print(f"Session: {session.id}")

    # Stream-first: open the stream BEFORE sending the kickoff message.
    with client.beta.sessions.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        )

        for event in stream:
            # Stream the agent's text output as it arrives.
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)

            # Respond to the get_user_dna tool call with the user's DNA Bible.
            elif event.type == "agent.custom_tool_use" and event.tool_name == "get_user_dna":
                dna = fetch_user_dna(user_id)
                client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": event.id,
                            "content": [{"type": "text", "text": dna}],
                        }
                    ],
                )

            # Correct idle-break gate: don't break on bare status_idle — it fires transiently
            # between parallel tool calls and while waiting on user.custom_tool_result.
            elif event.type == "session.status_idle":
                if event.stop_reason.type != "requires_action":
                    break
            elif event.type == "session.status_terminated":
                break

    print()  # newline after streamed output

    # Download any files the agent wrote to /mnt/session/outputs/.
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    files = client.beta.files.list(extra_query={"scope": session.id})
    for f in files.data:
        safe_name = os.path.basename(f.filename) or f.id
        target = out_path / safe_name
        content = client.beta.files.download(f.id)
        content.write_to_file(str(target))
        print(f"Saved: {target}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Humanizer on a document.")
    parser.add_argument("--user", required=True, help="User ID (for DNA Bible lookup)")
    parser.add_argument("--prompt", required=True, help="Writing instruction for the agent")
    parser.add_argument("--input", help="Optional path to input document to upload")
    parser.add_argument("--output-dir", default="./outputs", help="Where to save generated files")
    args = parser.parse_args()

    humanize(
        user_id=args.user,
        prompt=args.prompt,
        document_path=args.input,
        output_dir=args.output_dir,
    )
