# Humanizer — Claude Code skill

A globally-available [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills) that ports this repo's idea into a pure-prompt form: strip AI fingerprints and rewrite in a personal voice, with no Managed Agent or API call. Claude Code reads the reference files and applies them directly.

See `../docs/GLOBAL_SKILL.md` for how this maps to the Managed Agent implementation.

## Contents

```
skill/
├── SKILL.md                        # workflow + the tells that matter most
└── references/
    ├── writing_guardrails.md       # the AI-tell catalog (negative rules)
    └── leland_dna.md               # voice profile — SHIPPED AS A TEMPLATE here
```

## The DNA file is a template

`references/leland_dna.md` in this repo is the **unfilled template** (the same
content as `../dna_bible_template.md`), on purpose. Real, filled-in voice
profiles contain personal info, so they are **not committed** — the repo's
`.gitignore` excludes `user_dna/*.md` for the same reason.

The SKILL.md already handles an unfilled template: where a section still shows a
STARTER DEFAULT instead of a filled-in YOUR VERSION, it uses the default.

## Installing

The easiest path is the marketplace plugin, which includes a guided setup
(`humanizer-setup`) that builds your voice profile from your own writing and
stores it update-safe in `~/.claude/humanizer/`:

```
/plugin marketplace add Chameleon-Labs-LLC/plugins
/plugin install humanizer@chameleon-labs
```

Then say **"set up humanizer"**.

Manual alternative: copy the `skill/` contents into a skill directory and fill
in your own voice by hand:

```bash
mkdir -p ~/.claude/skills/humanizer
cp -r skill/SKILL.md skill/references ~/.claude/skills/humanizer/
# then edit ~/.claude/skills/humanizer/references/leland_dna.md — replace the
# YOUR VERSION lines with your own voice. Even one or two sections shifts the output.
```

Refine the voice profile over time: when a rewrite is off, adjust the relevant
section so the next one starts closer.
