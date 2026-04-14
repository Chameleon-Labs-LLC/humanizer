# Humanizer

A Managed Agent (Anthropic Claude API) that strips AI fingerprints from writing and replaces them with each user's personal voice.

Inspired by [Craig's NotebookLM + Gemini "AI Tell Eliminator"](https://www.notion.so/I-Built-This-NotebookLM-Gemini-Workflow-to-Destroy-AI-Fingerprints-335606421d12802da336fa1b41a04970). This project is the Claude + Managed Agents port, with per-user voice profiles served by a custom tool.

## How it works

Two reference documents drive every response:

1. **Writing Guardrails** (`writing_guardrails.md`) — over 200 banned words, phrases, sentence structures, punctuation habits, and formatting tells. Baked into the agent's system prompt, so it applies to every user equally.
2. **Text DNA Bible** (`user_dna/<user_id>.md`) — a personal voice profile per user. Covers rhythm, vocabulary, humor, formatting prefs, and content philosophy. Fetched via a custom tool at the start of every writing task.

The agent is a single persisted Anthropic [Managed Agent](https://platform.claude.com/docs/en/managed-agents/overview). Sessions are short-lived and per-request.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Your host app (run.py)                                    │
│  ├─ fetch_user_dna(user_id) → reads user_dna/<id>.md       │
│  └─ Calls client.beta.sessions.create(agent=AGENT_ID, ...) │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Anthropic orchestration (the agent loop runs here)        │
│                                                            │
│  Agent "Humanizer" (persisted, versioned)                  │
│  ├─ system: Writing Guardrails (~12KB, prompt-cached)      │
│  ├─ tools: read, write, edit, glob, grep                   │
│  └─ custom tool: get_user_dna (your app answers it)        │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│  Session container (sandboxed per-request)                 │
│  ├─ /workspace/input.*   — uploaded source document        │
│  └─ /mnt/session/outputs/ — agent writes rewritten files   │
└────────────────────────────────────────────────────────────┘
```

## Setup

**Prerequisites:** Python 3.10+, an Anthropic API key.

```bash
cd ~/code/agents/humanizer
python3 -m venv .venv_linux
source .venv_linux/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: add your ANTHROPIC_API_KEY

# one-time: create the environment and agent on Anthropic's side
python setup.py
# → prints HUMANIZER_ENV_ID and HUMANIZER_AGENT_ID — save them to .env
```

## Adding a user

Drop a filled-in DNA Bible at `user_dna/<user_id>.md`. Use `dna_bible_template.md` as a starting point:

```bash
cp dna_bible_template.md user_dna/user_123.md
# edit user_dna/user_123.md — fill in the "YOUR VERSION" sections
```

Users without a file fall back to the template's starter defaults.

## Usage

### CLI

```bash
python run.py \
  --user user_123 \
  --prompt "Rewrite /workspace/input.md into my voice. Save the result to /mnt/session/outputs/rewritten.md" \
  --input drafts/first-draft.md \
  --output-dir outputs/
```

### As a library

```python
from run import humanize

humanize(
    user_id="user_123",
    prompt="Write a 300-word LinkedIn post about $topic. Save it to /mnt/session/outputs/post.md",
    document_path=None,
    output_dir="./outputs",
)
```

## Updating the Guardrails

Edit `writing_guardrails.md`, then:

```bash
python update.py
```

This creates a new immutable agent version. New sessions pick it up automatically. To pin callers to the old version, replace the bare `agent_id` in `run.py` with `{"type": "agent", "id": AGENT_ID, "version": <old_version>}`.

## Project layout

```
humanizer/
├── README.md                   # this file
├── requirements.txt
├── .env.example                # copy to .env
├── .gitignore
├── writing_guardrails.md       # negative rules (same for all users)
├── dna_bible_template.md       # positive rules template (copy per user)
├── setup.py                    # ONE-TIME: create agent + environment
├── update.py                   # update agent config (bumps version)
├── run.py                      # per-request runtime
├── user_dna/                   # per-user DNA bibles (gitignored)
│   └── .gitkeep
└── docs/
    ├── ARCHITECTURE.md         # detailed design notes
    ├── CUSTOM_TOOL.md          # how get_user_dna works
    └── OPERATIONS.md           # updating, versioning, cost notes
```

## Swapping the DNA backend

`fetch_user_dna()` in `run.py` is the seam. Replace the filesystem stub with any datastore:

```python
def fetch_user_dna(user_id: str) -> str:
    row = db.query_one("SELECT dna_bible FROM users WHERE id = %s", (user_id,))
    return row["dna_bible"] or DEFAULT_DNA
```

Everything else stays the same.

## License

Private. Internal ChameleonLabs / Chameleon-Labs-LLC use only.

## Credits

- AI-fingerprint catalog adapted from [@CraigDoesAi's NotebookLM + Gemini workflow](https://www.notion.so/I-Built-This-NotebookLM-Gemini-Workflow-to-Destroy-AI-Fingerprints-335606421d12802da336fa1b41a04970).
- Built on Anthropic's [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) (beta).
