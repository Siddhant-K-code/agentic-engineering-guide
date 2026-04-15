"""
Ch. 4 — Context Windows
Assignment: Make the context window visible

Run this as-is. Then add a 4th turn that asks the model to recall
something from turn 1. Watch whether it does.

No API key needed. The mock server starts automatically in Ona.
To use a real model: add OPENAI_API_KEY as an Ona User Secret at
https://app.gitpod.io/ai?user-settings=secrets
The starter detects it and switches with no code changes.
Docs: https://ona.com/docs/ona/configuration/secrets/user-secrets
"""

import os
import json
from openai import OpenAI

# Auto-detects mock vs. real: if OPENAI_API_KEY is set, uses it directly.
# Otherwise falls back to the local mock server.
if os.environ.get("OPENAI_API_KEY"):
    client = OpenAI()
    print("Real OpenAI API detected.")
else:
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:8001/v1"),
        api_key="mock",
    )
    print("No API key found. Using mock server.")
    print("Add OPENAI_API_KEY as an Ona User Secret to use a real model.")
    print("https://app.gitpod.io/ai?user-settings=secrets\n")

MODEL = os.environ.get("MODEL", "gpt-4o-mini")

# Try to import tiktoken for accurate token counts; fall back to estimate.
try:
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-4o")
    def count_tokens(messages: list) -> int:
        total = 0
        for m in messages:
            total += 4  # per-message overhead
            total += len(enc.encode(str(m.get("content") or "")))
        return total
    print("tiktoken found. Token counts are accurate.\n")
except ImportError:
    def count_tokens(messages: list) -> int:
        # Rough estimate: 1 token per 4 chars
        raw = json.dumps(messages)
        return len(raw) // 4
    print("tiktoken not installed. Token counts are estimates.")
    print("Run: pip install tiktoken\n")


def print_context(messages: list, label: str = "") -> None:
    tokens = count_tokens(messages)
    bar = "─" * 56
    print(f"\n┌{bar}┐")
    header = f" Context window  {label}  ({len(messages)} messages, ~{tokens} tokens)"
    print(f"│{header:<56}│")
    print(f"├{bar}┤")
    for m in messages:
        role = m["role"].upper()
        content = str(m.get("content") or "")
        preview = content[:120].replace("\n", " ")
        if len(content) > 120:
            preview += "…"
        print(f"│ [{role:<9}] {preview:<44}│")
    print(f"└{bar}┘")


def chat(messages: list, user_message: str) -> str:
    messages.append({"role": "user", "content": user_message})
    print_context(messages, label="→ sending")

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    print_context(messages, label="← received")
    return reply


# ── Conversation ──────────────────────────────────────────────────────────────

messages = [
    {
        "role": "system",
        "content": (
            "You are a concise technical assistant. "
            "Keep answers to 2–3 sentences unless asked for more."
        ),
    }
]

print_context(messages, label="initial")

# Turn 1 — plant a specific fact early in the context
turn1 = chat(messages, "What is a context window? Give me one concrete number to remember.")
print(f"\nAssistant: {turn1}\n")

# Turn 2 — add noise in the middle
turn2 = chat(messages, "Why does the order of information in the context window matter?")
print(f"\nAssistant: {turn2}\n")

# Turn 3 — add more noise
turn3 = chat(messages, "What is the 'lost in the middle' problem?")
print(f"\nAssistant: {turn3}\n")

# ── Your turn ─────────────────────────────────────────────────────────────────
# Add a 4th turn. Ask the model to recall the specific number from turn 1.
# Does it remember?
#
#   turn4 = chat(messages, "What was the specific number you mentioned first?")
#   print(f"\nAssistant: {turn4}\n")
#
# Then add 5 to 10 more turns of unrelated content before asking again.
# Does recall degrade?
# ─────────────────────────────────────────────────────────────────────────────

print("\n── Summary ──────────────────────────────────────────────────────────────")
print(f"Messages in context : {len(messages)}")
print(f"Tokens used         : ~{count_tokens(messages)}")
print(f"Turns completed     : {(len(messages) - 1) // 2}")
print()
print("Questions to answer:")
print("  1. At what turn did recall start to degrade?")
print("  2. Which messages would you drop first to stay under budget?")
