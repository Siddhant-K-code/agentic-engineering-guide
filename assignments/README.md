# Practical Track — Assignments

Hands-on companion to [agents.siddhantkhare.com](https://agents.siddhantkhare.com).

Each chapter has a runnable starter file and 2 constrained questions. No open-ended projects. Modify the starter, run it, answer the questions.

## Quick start

### Option A — Open in Ona (recommended)

Click the badge on any chapter page, or open the full repo:

[![Run in Ona](https://ona.com/run-in-ona.svg)](https://app.gitpod.io/#https://github.com/Siddhant-K-code/agentic-engineering-assignments)

The environment starts pre-configured: Python 3.12, all dependencies installed, mock server running. No API key needed.

**To use a real model:** add `OPENAI_API_KEY` as an [Ona User Secret](https://app.gitpod.io/ai?user-settings=secrets). The starters detect it and switch with no code changes. [How to add a secret.](https://ona.com/docs/ona/configuration/secrets/user-secrets)

### Option B — Run locally

```bash
git clone https://github.com/Siddhant-K-code/agentic-engineering-assignments
cd agentic-engineering-assignments
./setup.sh        # creates venv, installs deps, starts mock server
```

Same behavior as the Ona environment. Set `OPENAI_API_KEY` in your shell to use a real model.

## Priority assignments (start here)

| Chapter | Assignment | Starter |
|---|---|---|
| [Ch. 4 — Context Windows](https://agents.siddhantkhare.com/04-context-windows/) | Make the context window visible | `ch04-context-windows/starter.py` |
| [Ch. 9 — Prompt Injection](https://agents.siddhantkhare.com/09-prompt-injection/) | Inject, observe, defend | `ch09-prompt-injection/starter.py` |
| [Ch. 17 — The Agent Loop](https://agents.siddhantkhare.com/17-agent-loop/) | Build a bare-metal agent loop | `ch17-agent-loop/starter.py` |

## Mock server

All starters work without an API key. The mock server (`mock-server/main.py`) mimics the OpenAI chat completions API with chapter-appropriate responses — realistic enough to observe the behavior each assignment surfaces.

```
OPENAI_BASE_URL=http://localhost:8001/v1
OPENAI_API_KEY=mock
```

The Ona environment and `setup.sh` set these automatically when no real key is present.

## Access

Assignments are available by tier. See [agents.siddhantkhare.com](https://agents.siddhantkhare.com) for pricing.
