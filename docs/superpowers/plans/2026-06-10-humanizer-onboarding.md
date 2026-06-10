# Humanizer Plugin Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a guided `humanizer-setup` skill to the published humanizer plugin that builds each user's voice profile in `~/.claude/humanizer/`, and wire all install docs to it.

**Architecture:** A second skill inside the existing `humanizer` plugin (in the `Chameleon-Labs-LLC/plugins` repo). The main skill resolves the voice profile from `~/.claude/humanizer/voice_profile.md` first, falling back to its bundled template. The setup skill creates that file and fills it by distilling user-approved writing samples (pasted text, selected disk files, selected sent emails). Docs in both repos point the personalize step at setup.

**Tech Stack:** Markdown skill files only — no code, no tests to run. Verification is structural (file existence, frontmatter, greps) plus a plugin validation pass.

**Spec:** `docs/superpowers/specs/2026-06-10-humanizer-onboarding-design.md` (this repo)

**Repos:**
- `/mnt/d/Documents/Code/GitHub/plugins` — marketplace plugin (Tasks 1-4)
- `/mnt/d/Documents/Code/GitHub/humanizer` — this repo, docs wiring (Task 5)

Both repos commit directly to `main` (Leland's convention for small projects/skills).

---

### Task 1: Create the `humanizer-setup` skill

**Files:**
- Create: `/mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer-setup/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `/mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer-setup/SKILL.md` with exactly this content:

````markdown
---
name: humanizer-setup
description: >-
  Builds or updates your personal voice profile for the humanizer skill. Use when
  the user says "set up humanizer", "set up my voice", "create my voice profile",
  "build my voice profile", "import my writing samples", "add this to my voice
  profile", or "update my voice profile" — or when the humanizer skill offered to
  build a profile and the user said yes. Walks the user through importing real
  writing samples (pasted text, files they pick, sent emails they select) and
  distills them into ~/.claude/humanizer/voice_profile.md, which survives plugin
  updates. Do NOT use for actually rewriting or drafting prose — that's the
  humanizer skill.
---

# Humanizer Setup

The humanizer skill rewrites prose to sound like a specific person. This skill builds the profile that tells it who that person is. It creates `~/.claude/humanizer/voice_profile.md` (outside the plugin, so plugin updates never touch it) and fills it by distilling the user's real writing.

Ground rules, and say them to the user up front: everything stays local under `~/.claude/humanizer/`. Nothing gets uploaded or shared. Disk and email access are opt-in, and the user picks every individual item that gets imported.

## Step 1: Name

Run `git config user.name`. Confirm with the user: "Should I build the profile for <first name>?" Use their first name from then on. Only ask for a name if git has no answer or they correct you.

## Step 2: Create the files

```bash
mkdir -p ~/.claude/humanizer/raw_samples
```

Copy the bundled template into place. The template lives in the sibling skill: `<this skill's base directory>/../humanizer/references/voice_profile.md`. Copy it to `~/.claude/humanizer/voice_profile.md`.

If `~/.claude/humanizer/voice_profile.md` already exists, don't overwrite it — treat this run as an update (see "Re-runs and updates").

Then edit the new file's header: retitle it `# TEXT DNA BIBLE — <First name>` and add a line directly under the title: `Last updated: <today's date>` (get the real date with `date '+%Y-%m-%d'`).

## Step 3: Gather writing samples

Best sources first. Offer the ones that apply and let the user choose. Save every imported sample to `~/.claude/humanizer/raw_samples/<short-name>.md` with a one-line header noting source and date.

**a. Direct.** Anything they paste or a file they point you at. The best samples are casual and real: posts, emails to friends or colleagues, blog paragraphs they're proud of. Formal documents they wrote to sound corporate are the worst samples — they hide the voice.

**b. Disk scan — ask first.** Offer: "Want me to look for writing of yours on disk? I'll show you a list and you pick. I won't import anything you don't choose." Good hunting grounds:

- READMEs and docs in their git repos where `git log --author="<name>" --format=%H -- <file>` shows they wrote it
- Blog-post folders: directories named `posts/`, `blog/`, `_posts/`, `content/`
- Social-media data exports in `~/Downloads` or `~/Documents`: LinkedIn exports (`Shares.csv`), Twitter/X archives (`tweets.js`)
- `~/Documents` for essays, newsletters, talks

Present candidates as a list (path, first line, modified date). Import only what they select. Never import an unselected file.

**c. Sent email — ask first, and only if available.** Check your available tools for a connected email integration (Gmail, Outlook, or similar MCP). If there is none, skip this option silently — don't advertise it. If there is one:

1. Ask permission explicitly: "I can pull a few of your sent emails as voice samples. Want me to search your sent mail and show you candidates to pick from?"
2. Search **sent** mail only — never the inbox, never anyone else's words.
3. Show a candidate list: subject, date, first line.
4. Import only the messages the user selects.
5. Before saving, strip quoted replies, signatures, and legal footers. Only the user's own words go in the profile.

**No samples at all?** Fall back to interview-only (the Step 4 questions). The result is still far better than the raw template.

## Step 4: Distill

Samples are *evidence of voice*, not text to copy. Read them looking for:

- Rhythm: sentence lengths, fragments, parentheticals, how bursty the writing is
- Vocabulary: pet words, plain vs. fancy, contractions, idioms
- Punctuation and emoji habits
- How they open and how they close
- Directness, hedging, humor, warmth

Fill in the matching numbered sections of the profile, replacing each YOUR VERSION line you have evidence for. Quote tiny phrases from the samples as examples, the way a style guide would. Leave STARTER DEFAULTS in place for sections with no evidence.

Then interview for what samples can't show — at most 3-4 questions, asked one at a time, skipping anything the samples already answered:

1. Humor: "Where's your humor, on a dial from deadpan to goofy? Anywhere it's off-limits?"
2. Pet peeves: "What words or writing habits make you cringe when you read them?"
3. Philosophy: "What should your writing do to the reader?"

## Step 5: Finish

1. Update the `Last updated` stamp.
2. Play back a 3-5 line summary of the voice you captured ("short sentences, lots of parentheticals, dry humor, no emoji...") and ask if that sounds like them. Fix what they correct.
3. Offer a test drive: take a short AI-flavored paragraph and rewrite it in their new voice with the humanizer skill.

## Re-runs and updates

"Add this post to my voice profile" or "update my voice profile": save the new sample to `raw_samples/`, re-read the profile, adjust only the sections the new evidence changes, and update the stamp. Small corrections during normal humanizer use ("I'd never say that") are folded in directly by the humanizer skill; this skill is for sample imports and bigger refreshes.

## Privacy rules

- Everything lives under `~/.claude/humanizer/`. Nothing is uploaded, posted, or shared anywhere.
- Never import a file or email the user didn't explicitly select.
- Sent mail only, never the inbox. Strip other people's quoted words — only the user's writing belongs in their profile.
- If `~/.claude/humanizer/` can't be created or written, say so and stop. The humanizer skill keeps working from its bundled template.
````

- [ ] **Step 2: Verify structure**

Run: `head -15 /mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer-setup/SKILL.md`
Expected: YAML frontmatter opening `---`, `name: humanizer-setup`, `description: >-` block.

Run: `grep -c "ask first\|Ask permission\|opt-in\|didn't explicitly select" /mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer-setup/SKILL.md`
Expected: 4 or more (consent language present).

- [ ] **Step 3: Commit**

```bash
git -C /mnt/d/Documents/Code/GitHub/plugins add humanizer/skills/humanizer-setup/SKILL.md
git -C /mnt/d/Documents/Code/GitHub/plugins commit -m "feat(humanizer): add humanizer-setup skill for guided voice-profile onboarding

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Update the main humanizer skill (profile resolution + nudge + feedback folding)

**Files:**
- Modify: `/mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer/SKILL.md`

Four edits. Old strings are exact and currently unique in the file.

- [ ] **Step 1: Update the reference-files bullet**

Replace:

```markdown
- **`references/voice_profile.md`** — the user's voice profile. Rhythm, vocabulary, humor, how they open and close, what they value in writing. These are positive rules: the target the rewrite aims for.
```

With:

```markdown
- **The voice profile** — `~/.claude/humanizer/voice_profile.md` if it exists, otherwise the bundled `references/voice_profile.md` template. Rhythm, vocabulary, humor, how they open and close, what they value in writing. These are positive rules: the target the rewrite aims for.
```

- [ ] **Step 2: Replace the "Make it yours first" section**

Replace:

```markdown
## Make it yours first

`references/voice_profile.md` ships as a template with sane STARTER DEFAULTS and a YOUR VERSION line under each section. It works out of the box, but it gets dramatically better once the user fills in even a section or two with their actual voice. If the output sounds generic, the fix is almost always a richer voice profile — point the user at that file. A pasted writing sample (a post, an email, a paragraph they're proud of) is the fastest way to fill it in well.
```

With:

```markdown
## The voice profile

Resolve the profile in this order:

1. **`~/.claude/humanizer/voice_profile.md`** — the user's personal profile, built by the `humanizer-setup` skill. It lives outside the plugin on purpose: plugin updates never overwrite it.
2. **`references/voice_profile.md`** — the bundled template with sane STARTER DEFAULTS. A workable baseline, but it's nobody's actual voice.

If you fall back to the template on a real writing task, offer once (not on every task): "Want me to build your voice profile from your actual writing? Say *set up humanizer*." Then get on with the writing — the template still works.
```

- [ ] **Step 3: Update "How to do it" step 2**

Replace:

```markdown
2. **Read `references/voice_profile.md`.** This is your target voice. Where a section still shows a STARTER DEFAULT rather than a filled-in YOUR VERSION, use the default — it's a sane baseline — but know the filled-in sections carry more weight.
```

With:

```markdown
2. **Read the voice profile** (resolved per "The voice profile" above). This is your target voice. Where a section still shows a STARTER DEFAULT rather than a filled-in YOUR VERSION, use the default — it's a sane baseline — but know the filled-in sections carry more weight.
```

- [ ] **Step 4: Update the feedback-folding section**

Replace:

```markdown
## Updating the voice profile

The voice profile improves over time. If the user reacts to a rewrite ("too stiff," "I'd never say 'leverage'," "that's exactly right"), that's signal — fold it into `references/voice_profile.md` so the next rewrite starts closer. The guardrails file rarely changes; the voice file is meant to.
```

With:

```markdown
## Updating the voice profile

The voice profile improves over time. If the user reacts to a rewrite ("too stiff," "I'd never say 'leverage'," "that's exactly right"), that's signal — fold it into `~/.claude/humanizer/voice_profile.md` so the next rewrite starts closer. If that file doesn't exist yet, copy the bundled template there first, then fold the correction in. Never write corrections into the bundled `references/voice_profile.md` — plugin updates overwrite it. The guardrails file rarely changes; the voice file is meant to.
```

- [ ] **Step 5: Verify**

Run: `grep -c "~/.claude/humanizer/voice_profile.md" /mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer/SKILL.md`
Expected: 4

Run: `grep -c "Make it yours first" /mnt/d/Documents/Code/GitHub/plugins/humanizer/skills/humanizer/SKILL.md`
Expected: 0

- [ ] **Step 6: Commit**

```bash
git -C /mnt/d/Documents/Code/GitHub/plugins add humanizer/skills/humanizer/SKILL.md
git -C /mnt/d/Documents/Code/GitHub/plugins commit -m "feat(humanizer): resolve voice profile from ~/.claude/humanizer/ with template fallback

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Bump plugin metadata and rewrite the plugin README

**Files:**
- Modify: `/mnt/d/Documents/Code/GitHub/plugins/humanizer/.claude-plugin/plugin.json`
- Modify: `/mnt/d/Documents/Code/GitHub/plugins/.claude-plugin/marketplace.json` (humanizer entry, ~lines 61-67)
- Modify: `/mnt/d/Documents/Code/GitHub/plugins/humanizer/README.md`

- [ ] **Step 1: plugin.json**

In `/mnt/d/Documents/Code/GitHub/plugins/humanizer/.claude-plugin/plugin.json`, replace:

```json
  "description": "Strips AI fingerprints from writing and rewrites it in your own voice. A catalog of 200+ AI tells to avoid plus a fill-in-yourself voice profile, applied to clean up AI-sounding text or to draft fresh prose that doesn't read like a chatbot wrote it.",
  "version": "0.1.0",
```

With:

```json
  "description": "Strips AI fingerprints from writing and rewrites it in your own voice. A catalog of 200+ AI tells to avoid plus a personal voice profile, applied to clean up AI-sounding text or to draft fresh prose that doesn't read like a chatbot wrote it. Includes a guided setup that builds your voice profile from your own writing.",
  "version": "0.2.0",
```

- [ ] **Step 2: marketplace.json**

In `/mnt/d/Documents/Code/GitHub/plugins/.claude-plugin/marketplace.json`, in the `"name": "humanizer"` entry, make the same two changes: the same new description string, and `"version": "0.2.0"`.

- [ ] **Step 3: README — replace "Make it yours" section**

In `/mnt/d/Documents/Code/GitHub/plugins/humanizer/README.md`, replace:

```markdown
## Make it yours

`voice_profile.md` ships as a template with sane defaults and a `YOUR VERSION` line under each section. It works out of the box, but it gets much better once you fill in even a section or two with your actual voice. The fastest way: paste a paragraph you've written and are happy with, and let the skill fill the profile from it.
```

With:

```markdown
## Make it yours

After installing, say **"set up humanizer"**. A guided setup builds your personal voice profile from your real writing: samples you paste, files on disk you pick from a list, or sent emails you select (only if you have an email integration connected, and only the messages you choose). Your profile is saved to `~/.claude/humanizer/voice_profile.md`, outside the plugin, so plugin updates never overwrite it.

Skip setup and it still works — the bundled template has sane defaults. But even one real writing sample makes the output noticeably more you.
```

- [ ] **Step 4: README — update the install closer and the How-it-works table**

Replace:

```markdown
Then ask Claude to "humanize this" or "write this in my voice." Edit `voice_profile.md` to teach it who you are.
```

With:

```markdown
Then say **"set up humanizer"** to build your voice profile, and ask Claude to "humanize this" or "write this in my voice."
```

And in the "How it works" table, replace:

```markdown
| `skills/humanizer/references/voice_profile.md` | Your personal voice profile (the positive rules) |
```

With:

```markdown
| `~/.claude/humanizer/voice_profile.md` | Your personal voice profile, built by setup (the positive rules; a bundled template is the fallback) |
```

- [ ] **Step 5: Verify**

Run: `python3 -c "import json; [json.load(open(p)) for p in ['/mnt/d/Documents/Code/GitHub/plugins/humanizer/.claude-plugin/plugin.json','/mnt/d/Documents/Code/GitHub/plugins/.claude-plugin/marketplace.json']]; print('json ok')"`
Expected: `json ok`

Run: `grep -rn "0.1.0" /mnt/d/Documents/Code/GitHub/plugins/humanizer/.claude-plugin/plugin.json /mnt/d/Documents/Code/GitHub/plugins/.claude-plugin/marketplace.json | grep humanizer`
Expected: no output (only other plugins may still be 0.1.0 in marketplace.json).

- [ ] **Step 6: Commit**

```bash
git -C /mnt/d/Documents/Code/GitHub/plugins add humanizer/.claude-plugin/plugin.json .claude-plugin/marketplace.json humanizer/README.md
git -C /mnt/d/Documents/Code/GitHub/plugins commit -m "feat(humanizer): v0.2.0 — guided setup; docs point at it

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Validate the plugin

**Files:** none (read-only check)

- [ ] **Step 1: Run the plugin validator**

Dispatch the `plugin-dev:plugin-validator` agent on `/mnt/d/Documents/Code/GitHub/plugins/humanizer` (it checks plugin.json schema, skill frontmatter, and file structure).
Expected: no errors. Warnings about optional fields are acceptable.

- [ ] **Step 2: Fix anything it flags, amend the Task 3 commit if trivial, or commit a fix**

```bash
git -C /mnt/d/Documents/Code/GitHub/plugins add -A humanizer .claude-plugin
git -C /mnt/d/Documents/Code/GitHub/plugins commit -m "fix(humanizer): address plugin validation findings

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(Skip this commit if validation passed clean.)

---

### Task 5: Docs wiring in the humanizer repo

**Files:**
- Modify: `/mnt/d/Documents/Code/GitHub/humanizer/README.md` (skill install paragraph, ~lines 9-16)
- Modify: `/mnt/d/Documents/Code/GitHub/humanizer/skill/README.md` (Installing section)
- Modify: `/mnt/d/Documents/Code/GitHub/humanizer/docs/GLOBAL_SKILL.md`

- [ ] **Step 1: Main README**

In `/mnt/d/Documents/Code/GitHub/humanizer/README.md`, after the install code block (`/plugin install humanizer@chameleon-labs`), replace:

```markdown
Or copy the skill straight from this repo's [`skill/`](skill/) folder. See [`docs/GLOBAL_SKILL.md`](docs/GLOBAL_SKILL.md) for details.
```

With:

```markdown
After installing, say **"set up humanizer"** — a guided setup builds your voice profile from your own writing (samples you paste, files you pick, or sent emails you select). Or copy the skill straight from this repo's [`skill/`](skill/) folder and fill in the template by hand. See [`docs/GLOBAL_SKILL.md`](docs/GLOBAL_SKILL.md) for details.
```

- [ ] **Step 2: skill/README.md Installing section**

In `/mnt/d/Documents/Code/GitHub/humanizer/skill/README.md`, replace:

```markdown
## Installing

Copy the `skill/` contents into a skill directory and fill in your own voice:
```

With:

```markdown
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
```

(The existing `mkdir/cp` code block and the comment lines after it stay as they are.)

- [ ] **Step 3: docs/GLOBAL_SKILL.md**

Add this section at the end of `/mnt/d/Documents/Code/GitHub/humanizer/docs/GLOBAL_SKILL.md`:

```markdown
## Public plugin onboarding (v0.2.0)

The marketplace plugin (`humanizer@chameleon-labs`, in the
`Chameleon-Labs-LLC/plugins` repo) ships a second skill, `humanizer-setup`,
that builds a new user's voice profile interactively: name from `git config`,
writing samples imported with per-item consent (pasted text, selected disk
files, selected sent emails), distilled into
`~/.claude/humanizer/voice_profile.md`. That file lives outside the plugin
cache so plugin updates never overwrite it; the bundled template is the
fallback.

That flow is for plugin users. Leland's personal skill at
`~/.claude/skills/humanizer/` keeps its own sync procedure (see "Keeping the
voice profile in sync" above) and is unaffected.

Design spec: `docs/superpowers/specs/2026-06-10-humanizer-onboarding-design.md`.
```

- [ ] **Step 4: Verify**

Run: `grep -rn "set up humanizer" /mnt/d/Documents/Code/GitHub/humanizer/README.md /mnt/d/Documents/Code/GitHub/humanizer/skill/README.md /mnt/d/Documents/Code/GitHub/humanizer/docs/GLOBAL_SKILL.md | wc -l`
Expected: 3 or more

- [ ] **Step 5: Commit**

```bash
git -C /mnt/d/Documents/Code/GitHub/humanizer add README.md skill/README.md docs/GLOBAL_SKILL.md
git -C /mnt/d/Documents/Code/GitHub/humanizer commit -m "docs: wire install docs to the plugin's guided humanizer-setup flow

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: End-to-end smoke test of the fallback logic (manual walkthrough)

**Files:** none

The spec's "fresh install" test can't fully run without reinstalling the plugin, but the resolution logic can be sanity-checked from the files:

- [ ] **Step 1: Fallback path** — confirm `~/.claude/humanizer/voice_profile.md` does NOT exist on this machine (Leland uses the personal skill, not the plugin): `ls ~/.claude/humanizer/ 2>&1`. Expected: "No such file or directory". This is the state a fresh plugin user is in, and the main skill's "The voice profile" section explicitly handles it (template + one-time nudge).
- [ ] **Step 2: Path consistency** — every mention of the user profile across the plugin resolves to the same path: `grep -rn "humanizer/voice_profile.md" /mnt/d/Documents/Code/GitHub/plugins/humanizer/ | grep -v "references/voice_profile.md"`. Expected: all hits read `~/.claude/humanizer/voice_profile.md`, no variants.
- [ ] **Step 3: Template untouched** — `git -C /mnt/d/Documents/Code/GitHub/plugins diff HEAD~3 --stat -- humanizer/skills/humanizer/references/`. Expected: no changes to the references directory.

---

## Self-review notes

- Spec coverage: profile resolution + nudge + feedback folding (Task 2), setup skill with name/files/samples/distill/re-runs/privacy (Task 1), version + description (Task 3), docs wiring incl. both repos (Tasks 3, 5), error handling lives inside the Task 1 skill text (no email tool → skip silently; unwritable dir → stop and say so; no samples → interview-only), testing (Tasks 4, 6). "Use first name" spec edit is in Task 1 Step 1 (Step 1: Name) and the retitle instruction.
- Out of scope honored: no changes to the Managed Agent, `~/.claude/skills/humanizer/`, or `references/voice_profile.md` template content.
