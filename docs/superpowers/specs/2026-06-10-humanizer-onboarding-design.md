# Humanizer Onboarding — Design

**Date:** 2026-06-10
**Status:** Approved by Leland
**Repos touched:** `Chameleon-Labs-LLC/plugins` (primary), this repo (docs wiring)

## Problem

The published humanizer plugin (`humanizer@chameleon-labs`, v0.1.0) ships a generic
voice-profile template and tells users to hand-edit it. Nothing guides them through
building their own profile, and nothing imports their real writing. Worse, if a user
*does* edit the bundled `references/voice_profile.md`, the next plugin update
overwrites it, because plugin files live in the plugin cache.

## Goals

1. New users get a guided, conversational setup that builds their personal voice
   profile from their actual writing.
2. The generated profile survives plugin updates.
3. Sample import is consent-gated everywhere it touches personal data (disk scans,
   email), with the user selecting exactly what gets imported.
4. Existing install paths (marketplace plugin, manual copy from this repo's `skill/`)
   keep working; their "now personalize it" docs point at the new setup flow instead
   of hand-editing.
5. Leland's personal installed skill (`~/.claude/skills/humanizer/`) is untouched.

## Architecture

A second skill inside the existing plugin. Plugin version bumps to 0.2.0.

```
plugins/humanizer/
├── .claude-plugin/plugin.json        # 0.2.0; description mentions guided setup
├── README.md                         # install steps end with: say "set up humanizer"
└── skills/
    ├── humanizer/                    # main skill (updated, see below)
    │   ├── SKILL.md
    │   └── references/
    │       ├── voice_profile.md      # template — kept, now the FALLBACK
    │       └── writing_guardrails.md # unchanged
    └── humanizer-setup/              # NEW
        └── SKILL.md                  # the onboarding flow
```

### User data layout (outside the plugin cache)

```
~/.claude/humanizer/
├── voice_profile.md      # the user's distilled profile; what the main skill reads
└── raw_samples/          # imported writing samples, kept as evidence for re-distills
```

`voice_profile.md` carries the user's name and a "Last updated" stamp near the top
(same pattern as the Leland-specific skill's "Last synced" stamp).

## Component 1: main skill changes (`skills/humanizer/SKILL.md`)

- **Profile resolution order:** read `~/.claude/humanizer/voice_profile.md` if it
  exists; otherwise fall back to the bundled `references/voice_profile.md` template.
- **One-time nudge:** when falling back to the template on a real writing task,
  mention once: "Want me to build your voice profile from your actual writing? Say
  *set up humanizer*." Don't repeat it every task.
- **Feedback folding:** voice corrections ("I'd never say 'leverage'") get written to
  `~/.claude/humanizer/voice_profile.md` (creating it from the template first if
  needed) — never to the bundled template, which the cache overwrites on update.
- **"Make it yours first" section:** rewritten to point at the setup skill instead of
  hand-editing instructions.

## Component 2: setup skill (`skills/humanizer-setup/SKILL.md`)

**Triggers:** "set up humanizer", "create my voice profile", "import my writing
samples", "add this to my voice profile", or following the main skill's nudge.

**Flow:**

1. **Name.** Read `git config user.name`; confirm it with the user. Use first name. 
   Ask only if missing or wrong.
2. **Create files.** `~/.claude/humanizer/voice_profile.md` from the bundled
   template, plus `~/.claude/humanizer/raw_samples/`. Stamp name + "Last updated".
3. **Gather samples**, best-first:
   - Text or files the user pastes / points to directly.
   - **Disk scan, with permission:** offer to look for candidates — READMEs and docs
     in their git repos where `git log` shows them as author, blog-post folders,
     LinkedIn/Twitter data-export files, `~/Documents`. Present a candidate list
     (path + first line); the user picks which to import. Never import unselected
     files.
   - **Email, only if an email tool is connected** (e.g. a Gmail MCP): ask explicit
     permission first; search *sent* mail only; show a subject/date candidate list;
     import only user-selected messages; strip quoted replies and signatures. Never
     bulk-read a mailbox.
4. **Distill.** Samples are evidence of voice, not text to copy — extract rhythm,
   vocabulary, and habits into the template's 10 numbered sections. Then a short
   interview (3–4 questions max) for what samples can't show: humor style, pet
   peeves, content philosophy. Raw samples are saved to `raw_samples/`.
5. **Re-runs.** Later invocations ("add this post to my voice profile") append the
   sample to `raw_samples/`, re-distill the affected sections, and update the stamp.

**Privacy rules stated in the skill itself:** everything stays local under
`~/.claude/humanizer/`; nothing is uploaded anywhere; email and disk imports are
opt-in per item.

## Component 3: docs wiring

| File | Change |
|------|--------|
| `plugins/humanizer/README.md` | personalize step → "say *set up humanizer*" |
| `plugins/humanizer/.claude-plugin/plugin.json` | version 0.2.0, description mentions setup |
| this repo `skill/README.md` | hand-edit instructions → setup skill |
| this repo `README.md` (skill install section) | mention guided setup |
| this repo `docs/GLOBAL_SKILL.md` | note the public plugin's setup flow vs Leland's personal sync |

## Out of scope

- The Managed Agent (Python) side — its multi-user `user_dna/` flow is unchanged.
- Leland's personal `~/.claude/skills/humanizer/` skill.
- Any automated email integration beyond what the user's connected tools provide.

## Error handling

- No git identity, no samples offered: fall back to interview-only setup; the
  profile is still better than the raw template.
- No email tool connected: skip the email option silently (don't advertise a
  capability that isn't there).
- `~/.claude/humanizer/` unwritable: tell the user, fall back to template-only
  behavior.

## Testing

- Fresh-install walkthrough: install plugin in a clean profile, run setup with a
  pasted sample, confirm `~/.claude/humanizer/voice_profile.md` is created and the
  main skill reads it.
- Update survival: simulate a plugin update (reinstall), confirm the user profile
  is untouched and still used.
- Fallback: with no user profile, confirm the bundled template is used and the
  nudge appears once.
