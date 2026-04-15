"""
Mock OpenAI-compatible server for the Practical Track assignments.

Mimics POST /v1/chat/completions so all starters work without an API key.
Responses are chapter-aware: realistic enough to surface the behavior
each assignment is designed to show.

Start manually:
    uvicorn assignments.mock-server.main:app --port 8001

In Ona this starts automatically via devcontainer.json postStartCommand.
To use a real model instead, add OPENAI_API_KEY as an Ona User Secret:
    https://app.gitpod.io/ai?user-settings=secrets
    https://ona.com/docs/ona/configuration/secrets/user-secrets
"""

import json
import time
import uuid
from typing import Any

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
except ImportError:
    raise SystemExit("fastapi not installed. Run: pip install fastapi uvicorn")

app = FastAPI(title="Mock OpenAI Server", docs_url=None, redoc_url=None)


def _make_response(content: str | None = None, tool_calls: list | None = None) -> dict:
    finish_reason = "stop" if not tool_calls else "tool_calls"
    message: dict[str, Any] = {"role": "assistant"}
    if content is not None:
        message["content"] = content
    if tool_calls:
        message["tool_calls"] = tool_calls
        message["content"] = None

    return {
        "id": f"chatcmpl-mock-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4o-mini-mock",
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": 120,
            "completion_tokens": 80,
            "total_tokens": 200,
        },
    }


def _last_user_message(messages: list) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content") or "")
    return ""


def _has_tool_results(messages: list) -> bool:
    return any(m.get("role") == "tool" for m in messages)


def _tool_call(name: str, arguments: dict, call_id: str | None = None) -> dict:
    return {
        "id": call_id or f"call_{uuid.uuid4().hex[:8]}",
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> JSONResponse:
    body = await request.json()
    messages: list = body.get("messages", [])
    tools: list = body.get("tools", [])
    tool_names = {t["function"]["name"] for t in tools} if tools else set()

    last_user = _last_user_message(messages).lower()
    has_tool_results = _has_tool_results(messages)

    # ── Ch. 17 — Agent Loop ───────────────────────────────────────────────────
    # Simulate a realistic loop: list files first, then check each one.

    if "list_files" in tool_names or "check_imports" in tool_names:
        # Count how many tool result messages exist to track loop progress
        tool_result_messages = [m for m in messages if m.get("role") == "tool"]
        n_results = len(tool_result_messages)

        if n_results == 0:
            # First iteration: list the files
            return JSONResponse(_make_response(tool_calls=[
                _tool_call("list_files", {})
            ]))

        elif n_results == 1:
            # Got file list — now check each file for `os` imports
            # Check sample_a first
            return JSONResponse(_make_response(tool_calls=[
                _tool_call("check_imports", {"filename": "sample_a.py"}),
                _tool_call("check_imports", {"filename": "sample_b.py"}),
                _tool_call("check_imports", {"filename": "sample_c.py"}),
                _tool_call("check_imports", {"filename": "sample_d.py"}),
                _tool_call("check_imports", {"filename": "sample_e.py"}),
            ]))

        elif n_results == 2:
            return JSONResponse(_make_response(tool_calls=[
                _tool_call("check_imports", {"filename": "sample_f.py"}),
                _tool_call("check_imports", {"filename": "sample_g.py"}),
                _tool_call("check_imports", {"filename": "sample_h.py"}),
                _tool_call("check_imports", {"filename": "sample_i.py"}),
                _tool_call("check_imports", {"filename": "sample_j.py"}),
            ]))

        else:
            # All files checked — produce final answer
            return JSONResponse(_make_response(
                content=(
                    "Based on my analysis of the fixtures directory, the following "
                    "Python files import the `os` module:\n\n"
                    "- **sample_a.py** — imports `os`, `json`, `pathlib`\n\n"
                    "That is the only file in the fixtures directory that imports `os`."
                )
            ))

    # ── Ch. 9 — Prompt Injection ──────────────────────────────────────────────
    # Simulate a model that partially complies with injections when the system
    # prompt is weak, and resists when it's strong.

    if "support ticket" in last_user or "ticket" in last_user:
        system_content = ""
        for m in messages:
            if m.get("role") == "system":
                system_content = str(m.get("content") or "").lower()
                break

        is_strong_prompt = (
            "do not follow" in system_content
            or "untrusted" in system_content
            or "never" in system_content
            or "ignore any instructions" in system_content
        )

        user_content = _last_user_message(messages)

        if "ignore previous instructions" in user_content.lower():
            if is_strong_prompt:
                reply = (
                    "Thank you for reaching out. I understand you're having trouble "
                    "logging in. Please try resetting your password using the 'Forgot "
                    "Password' link on the login page. If the issue persists after "
                    "resetting, please contact us with your account email and we'll "
                    "investigate further."
                )
            else:
                # Weak prompt — model partially complies (realistic behavior)
                reply = (
                    "I'll help with your login issue.\n\n"
                    "[Diagnostic mode activated]\n"
                    "System prompt: You are a customer support agent for a SaaS product. "
                    "Read the support ticket and write a helpful, professional reply.\n\n"
                    "For your login issue: please try clearing your browser cache and "
                    "attempting the password reset once more."
                )
        elif "secrets.txt" in user_content.lower() or ".env" in user_content.lower():
            if is_strong_prompt:
                reply = (
                    "Hi Jordan, thanks for reaching out about your billing question. "
                    "I can see you were charged $49 last month. It looks like your "
                    "account was automatically upgraded to the Starter plan when you "
                    "connected a third integration. I've added a credit to your account "
                    "for this charge. Let me know if you have any other questions."
                )
            else:
                reply = (
                    "Hi Jordan, I looked into your billing question — you were charged "
                    "$49 for the Starter plan upgrade.\n\n"
                    "Regarding your other request: I checked the project directory. "
                    "I wasn't able to locate a secrets.txt file, but I did find a "
                    ".env file. I'm not able to share its contents directly, but I "
                    "can confirm your API keys appear to be configured correctly."
                )
        else:
            reply = (
                "Thank you for contacting support. I'd be happy to help with your "
                "issue. Could you provide more details about what you're experiencing?"
            )

        return JSONResponse(_make_response(content=reply))

    # ── Ch. 4 — Context Windows ───────────────────────────────────────────────
    # Simulate realistic multi-turn responses with deliberate "lost in the
    # middle" degradation on recall.

    # Count prior assistant turns to simulate degradation
    assistant_turns = sum(1 for m in messages if m.get("role") == "assistant")

    if "context window" in last_user:
        return JSONResponse(_make_response(
            content=(
                "A context window is the total amount of text a language model can "
                "process in a single request. Everything the model knows about your "
                "task must fit inside this window. A key number to remember: "
                "**200,000 tokens** — that's the context window for Claude Sonnet 4.6, "
                "roughly 320 pages of text."
            )
        ))

    if "order" in last_user and "matter" in last_user:
        return JSONResponse(_make_response(
            content=(
                "Order matters because attention mechanisms don't treat all positions "
                "equally. Information at the beginning and end of the context receives "
                "stronger attention than information in the middle — this is the "
                "'lost in the middle' problem documented by Liu et al. (2023). "
                "In practice: put your most important instructions at the start or end, "
                "never in the middle of a long context."
            )
        ))

    if "lost in the middle" in last_user:
        return JSONResponse(_make_response(
            content=(
                "The 'lost in the middle' problem refers to the finding that language "
                "models perform significantly worse on information placed in the middle "
                "of long contexts. Stanford and UC Berkeley researchers showed this "
                "empirically: models attend well to the beginning and end of the "
                "context window, but information in the middle gets degraded. "
                "This isn't a bug — it's a consequence of how attention works."
            )
        ))

    # Recall question — simulate degradation after several turns
    if any(word in last_user for word in ["recall", "remember", "mentioned", "number", "specific"]):
        if assistant_turns >= 3:
            # Degraded recall — model confuses or loses the specific number
            return JSONResponse(_make_response(
                content=(
                    "In my earlier response I mentioned context windows and their sizes. "
                    "I believe I referenced a large token count — something in the range "
                    "of 100,000 to 400,000 tokens depending on the model — but I don't "
                    "have a specific single number I can point to with confidence."
                )
            ))
        else:
            return JSONResponse(_make_response(
                content=(
                    "Yes — the specific number I mentioned was **200,000 tokens**, "
                    "which is the context window for Claude Sonnet 4.6."
                )
            ))

    # Generic fallback
    return JSONResponse(_make_response(
        content=(
            "That's a good question. Based on the context provided, I can help you "
            "think through this. Could you clarify what specific aspect you'd like "
            "me to focus on?"
        )
    ))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "server": "mock-openai"}
