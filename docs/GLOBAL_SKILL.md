# Global Humanizer Skill (Claude Code port)

This repo is the Managed Agent implementation. There is also a **Claude Code skill** that ports the same idea — strip AI fingerprints, write in a personal voice — into a globally-available skill, with no API call or Managed Agent required. Claude Code reads the reference files and applies them directly.

Created 2026-05-31 with the `skill-creator` skill.

## Where it lives

- Installed (live): `~/.claude/skills/humanizer/`
- Portable bundle: `~/.claude/skills/humanizer.skill`

```
~/.claude/skills/humanizer/
├── SKILL.md                        # workflow + the tells that matter most
└── references/
    ├── writing_guardrails.md       # copied verbatim from this repo (negative rules)
    └── leland_dna.md               # Leland's voice profile (positive rules)
```

## How it maps to this repo

| This repo (Managed Agent) | The skill |
|---------------------------|-----------|
| `writing_guardrails.md` baked into system prompt | `references/writing_guardrails.md` (verbatim copy) |
| `user_dna/<id>.md` fetched via `get_user_dna` tool | `references/leland_dna.md` (read directly) |
| `run.py` / `setup.py` / Anthropic orchestration | not needed — Claude Code applies the files itself |

The skill is single-user (Leland's voice). The Managed Agent stays multi-user.

## Keeping the voice profile in sync

`user_dna/leland_dna.md` (this repo, used by the Managed Agent) is the canonical
**raw** DNA — bio, profile notes, and pasted writing samples. The skill's
`references/leland_dna.md` is the **distilled** voice profile built from it.

As of 2026-06-10 the skill carries the sync procedure itself (SKILL.md, "Syncing
from the project DNA"). To use it, tell Claude Code "sync my DNA" (or that you
updated your DNA in the project): it reads the raw file, distills anything new
into the profile's numbered sections, and updates the profile's "Last synced"
stamp. New material goes into the raw file in this repo; the skill never edits
it, only reads from it. `skill/SKILL.md` in this repo mirrors the installed
SKILL.md.

Note: a DNA Bible describes *how* Leland writes, not biographical facts. The
bottom "BACKGROUND" section of `user_dna/leland_dna.md` holds the bio as context
only — those phrasings ("my journey began," etc.) are NOT a writing target.

## Iteration 1 results (skill-creator eval)

Three light/qualitative test cases (de-AI a LinkedIn post, write a fresh post,
de-AI a marketing email), each run with-skill vs baseline (vanilla Claude).

- Mechanical assertions: **with-skill 10/10, baseline 7/10.** Every baseline
  miss was an em-dash (2 of 3 cases) or a length overflow — the classic tells
  the guardrails exist to catch.
- Qualitative review approved all three with-skill outputs, with three small
  voice corrections folded back into the DNA: prefer plain phrasing over
  constructed cleverness, keep sign-offs plain ("Happy to show it to anyone"),
  and use real greetings ("Hey," / "Hi," / "Good morning" — never "Hey there").

Eval workspace: `~/.claude/skills/humanizer-workspace/iteration-1/`.
