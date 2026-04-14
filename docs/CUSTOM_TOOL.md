# The `get_user_dna` custom tool

This is how the agent asks the host app for the current user's voice profile.

## Wire format

### Tool definition (sent to Anthropic at agent-creation time)

```json
{
  "type": "custom",
  "name": "get_user_dna",
  "description": "Fetch the current user's Text DNA Bible — their personal voice profile covering rhythm, vocabulary, humor, formatting, and content philosophy. Call this at the start of every writing task before producing any output.",
  "input_schema": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

No inputs — the agent doesn't need to know the user ID. Your host app already knows which user a given session belongs to (you created the session).

### What the agent emits

```json
{
  "type": "agent.custom_tool_use",
  "id": "sevt_...",
  "tool_name": "get_user_dna",
  "input": {}
}
```

### What your app responds with

```json
{
  "type": "user.custom_tool_result",
  "custom_tool_use_id": "sevt_...",
  "content": [
    { "type": "text", "text": "<the user's DNA Bible contents>" }
  ]
}
```

`custom_tool_use_id` must be the `id` from the triggering event, not a `toolu_*` ID.

## Why it has no inputs

The alternative was:

```json
"input_schema": {"properties": {"user_id": {"type": "string"}}, "required": ["user_id"]}
```

Rejected because:

1. **The agent shouldn't know user IDs.** Your DB keys are not agent business. Passing them in means prompt-injection risk (a malicious input could convince the agent to fetch a different user's DNA).
2. **The session already knows.** Your host app creates the session for `user_123`; that binding stays host-side in a map from `session_id → user_id`.

In `run.py` the `humanize()` function closes over `user_id`, so `fetch_user_dna` is called with the right ID regardless of what the agent "asks for."

## Implementing the host-side lookup

The stub in `run.py` reads `user_dna/<user_id>.md`. In production you'd do something like:

### Option A: Postgres

```python
import psycopg

def fetch_user_dna(user_id: str) -> str:
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            "SELECT dna_bible FROM users WHERE id = %s", (user_id,)
        ).fetchone()
    return row[0] if row and row[0] else DEFAULT_DNA
```

### Option B: Prisma (if Humanizer ends up inside the ChameleonLabs monorepo)

```python
# Via a shared API surface — Humanizer would call a ChameleonLabs endpoint
import httpx

def fetch_user_dna(user_id: str) -> str:
    resp = httpx.get(
        f"{INTERNAL_API}/users/{user_id}/dna",
        headers={"x-service-key": SERVICE_KEY},
        timeout=5.0,
    )
    resp.raise_for_status()
    return resp.json()["dna_bible"] or DEFAULT_DNA
```

### Option C: S3

```python
import boto3

s3 = boto3.client("s3")

def fetch_user_dna(user_id: str) -> str:
    try:
        obj = s3.get_object(Bucket="chameleonlabs-humanizer-dna", Key=f"{user_id}.md")
        return obj["Body"].read().decode("utf-8")
    except s3.exceptions.NoSuchKey:
        return DEFAULT_DNA
```

Whichever you pick, two rules:

- **Fail safe.** A missing or corrupt DNA Bible should fall back to a default, not error out the session. The agent can still produce decent output from just the Guardrails.
- **Don't block.** If the DNA lookup takes more than a few seconds, the agent's session is just sitting there. Keep the lookup latency predictable (< 1s typical) and add a hard timeout.

## Rate limits

The custom tool call happens once per session. Humanizer sessions are one-shot (one user request per session), so the call rate matches your user request rate. No special throttling needed.

## Debugging

If you see the agent produce output that doesn't match the user's voice:

1. Log the raw tool result your app returned. Is the DNA file actually filled in, or is it still full of "YOUR VERSION" placeholders?
2. Log the `agent.custom_tool_use` event to confirm the agent is actually calling `get_user_dna`. If it's not, the system prompt isn't enforcing it; strengthen it.
3. Run the session with a DNA Bible that has very distinctive, extreme style rules (e.g. "every sentence must end with an exclamation point"). If that shows up in the output, the pipeline works and the issue is that the user's real DNA Bible is too generic.
