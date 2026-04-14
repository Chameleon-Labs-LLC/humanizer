# Operations

## First-time setup

```bash
python setup.py
```

Prints `HUMANIZER_ENV_ID` and `HUMANIZER_AGENT_ID`. Save both to `.env`. These are durable — they survive restarts, code deploys, everything.

## Updating the Guardrails

The Guardrails file is a living document. New AI tells get identified; old ones become less diagnostic. When you edit `writing_guardrails.md`:

```bash
python update.py
```

This calls `client.beta.agents.update()` which creates a new immutable version. The `agent_id` stays the same. New sessions pick up the latest version automatically (because `run.py` passes the bare `agent_id` string, which resolves to "latest").

### Pinning to a specific version

If a Guardrails change breaks something and you need old sessions to keep working:

```python
# In run.py, replace:
agent=agent_id

# With:
agent={"type": "agent", "id": agent_id, "version": 42}  # whatever version was good
```

Each `update.py` run prints the new version number. Save it somewhere if you might need to roll back.

### Listing versions

```python
for v in client.beta.agents.versions.list(agent_id=AGENT_ID):
    print(v.version, v.created_at)
```

## Changing the tool list

If you want to add or remove tools (e.g. enable `bash`, or add another custom tool):

1. Edit the `tools=[...]` list in `setup.py`.
2. Run `update.py` — but note that `update.py` currently only updates `system`. You'll need to modify it to pass `tools=` too, or delete and recreate the agent via `setup.py` (which requires a new `agent_id`).

Prefer the update path. Deleting the agent means new IDs everywhere.

## Cost monitoring

Each response event on the stream includes `model_usage` on `span.model_request_end`:

```json
{
  "type": "span.model_request_end",
  "model_usage": {
    "input_tokens": 312,
    "cache_read_input_tokens": 3891,
    "cache_creation_input_tokens": 0,
    "output_tokens": 427
  }
}
```

- `cache_read_input_tokens` is what you want to see high — that's the Guardrails being served from cache at ~10% of normal price.
- `cache_creation_input_tokens > 0` means the cache was cold; expected on the first session of each agent version.
- If `input_tokens` is high and `cache_read_input_tokens` is zero on the second and later requests, something is breaking the cache — most likely the Guardrails text shifted (trailing whitespace, reordered sections, etc). Diff the exact bytes sent.

## Environments: when to make a new one

The environment template governs the session container's networking and available packages. Make a new environment when:

- You want to restrict outbound networking (e.g. `{type: "package_managers_and_custom", allowed_hosts: [...]}`).
- You need specific packages pre-installed in the container (currently not used — Humanizer only touches text).

You can have multiple environments and pick one per session. For now, one is fine.

## Deleting an agent

You can't hard-delete an agent — only archive:

```python
client.beta.agents.archive(agent_id=AGENT_ID)
```

Archived agents are read-only. Existing sessions continue; new sessions can't be created. If you need a truly fresh start, archive the old one and run `setup.py` to make a new one.

## Session hygiene

Sessions auto-terminate when idle with `end_turn`. You don't need to explicitly delete them. If you're hitting storage limits or want to clean up:

```python
for s in client.beta.sessions.list():
    if s.status == "terminated":
        client.beta.sessions.delete(session_id=s.id)
```

## Rate limits

Managed Agents endpoints have separate per-organization RPM limits:

- Session/agent/vault creates: 60 RPM
- All other operations: 600 RPM
- Environment operations: 60 RPM with max 5 concurrent

Model inference inside a session still draws from your standard Messages API token limits. If you hit either, the Anthropic SDK auto-retries with exponential backoff (respects `retry-after`).

## Secrets

- `ANTHROPIC_API_KEY` — loaded from `.env` via `python-dotenv`. Never commit.
- `HUMANIZER_AGENT_ID`, `HUMANIZER_ENV_ID` — not secret, but `.env` is the right place for them so all config lives in one spot.

Per-user DNA Bibles contain personal writing samples. Store them server-side (filesystem, DB, S3) and treat them like any other user-provided content. They're in `.gitignore` by default.
