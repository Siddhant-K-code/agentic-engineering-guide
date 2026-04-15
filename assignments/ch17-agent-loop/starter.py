"""
Ch. 17 — The Agent Loop
Assignment: Build a bare-metal agent loop

No framework. Raw OpenAI SDK with explicit tool definitions. Loop state
prints at every iteration so you can see what the model decides and why.

Task: find all Python files in fixtures/ that import `os`. List them.

Run it. Count the iterations. Then:
  1. Could it have finished in fewer iterations? What caused the extras?
  2. Set MAX_ITERATIONS = 3 and re-run. What does it return at the limit?

No API key needed. The mock server starts automatically in Ona.
To use a real model: add OPENAI_API_KEY as an Ona User Secret at
https://app.gitpod.io/ai?user-settings=secrets
Docs: https://ona.com/docs/ona/configuration/secrets/user-secrets
"""

import os
import json
import ast
from pathlib import Path
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────

MAX_ITERATIONS = 10  # TASK: try setting this to 3

if os.environ.get("OPENAI_API_KEY"):
    client = OpenAI()
    print("Real OpenAI API detected.\n")
else:
    client = OpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:8001/v1"),
        api_key="mock",
    )
    print("No API key found. Using mock server.")
    print("Add OPENAI_API_KEY as an Ona User Secret to use a real model.")
    print("https://app.gitpod.io/ai?user-settings=secrets\n")

MODEL = os.environ.get("MODEL", "gpt-4o-mini")
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# ── Tools ─────────────────────────────────────────────────────────────────────
# Two tools: list_files and check_imports.
# The agent could answer in 2 tool calls: list files, then check each one.
# Watch whether it does, or whether it takes more.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all Python files in the fixtures directory.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_imports",
            "description": "Check which modules a Python file imports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename (e.g. sample_a.py) inside the fixtures directory.",
                    }
                },
                "required": ["filename"],
            },
        },
    },
]


def list_files() -> list[str]:
    return sorted(p.name for p in FIXTURES_DIR.glob("*.py"))


def check_imports(filename: str) -> dict:
    path = FIXTURES_DIR / filename
    if not path.exists():
        return {"error": f"{filename} not found"}
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as e:
        return {"error": str(e)}
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return {"filename": filename, "imports": sorted(set(imports))}


def dispatch_tool(name: str, args: dict) -> str:
    if name == "list_files":
        result = list_files()
    elif name == "check_imports":
        result = check_imports(**args)
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result)


# ── Loop state printer ────────────────────────────────────────────────────────

def print_iteration(iteration: int, decision: str, tool_calls: int, messages: list) -> None:
    # Rough token estimate: 1 token ≈ 4 chars
    tokens = sum(len(json.dumps(m)) // 4 for m in messages)
    print(
        f"  iteration {iteration:>2}  │  "
        f"tokens ~{tokens:<5}  │  "
        f"tool_calls_this_iter {tool_calls}  │  "
        f"decision: {decision}"
    )


# ── Agent loop ────────────────────────────────────────────────────────────────

TASK = (
    "Look at the Python files in the fixtures directory. "
    "Find all files that import the `os` module and return a list of their names."
)

messages = [
    {"role": "system", "content": "You are a precise code analysis assistant. Use the available tools to complete the task. Be efficient — use as few tool calls as necessary."},
    {"role": "user", "content": TASK},
]

print(f"Task: {TASK}\n")
print(f"{'─' * 72}")
print(f"  {'iter':>4}     {'tokens':>8}     {'tool calls':>12}     decision")
print(f"{'─' * 72}")

total_tool_calls = 0
final_answer = None

for iteration in range(1, MAX_ITERATIONS + 1):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    msg = response.choices[0].message
    finish_reason = response.choices[0].finish_reason

    # Count tool calls this iteration
    calls_this_iter = len(msg.tool_calls) if msg.tool_calls else 0
    total_tool_calls += calls_this_iter

    if finish_reason == "stop" or not msg.tool_calls:
        print_iteration(iteration, "final_answer", calls_this_iter, messages)
        final_answer = msg.content
        break

    print_iteration(iteration, "tool_call", calls_this_iter, messages)

    # Append assistant message with tool calls
    messages.append(msg)

    # Execute each tool call and append results
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments) if tc.function.arguments else {}
        result = dispatch_tool(tc.function.name, args)
        print(f"           └─ {tc.function.name}({json.dumps(args)}) → {result[:80]}")
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result,
        })
else:
    # Hit MAX_ITERATIONS without a final answer
    print_iteration(MAX_ITERATIONS, "MAX_ITERATIONS_REACHED", 0, messages)
    final_answer = (
        f"[Stopped at iteration limit ({MAX_ITERATIONS}). "
        "Partial context available — see messages above.]"
    )

print(f"{'─' * 72}\n")
print(f"Answer:\n{final_answer}\n")
print(f"{'─' * 72}")
print(f"Iterations          : {iteration}")
print(f"Tool calls          : {total_tool_calls}")
print(f"Messages in context : {len(messages)}")
print(f"{'─' * 72}\n")
print("Questions to answer:")
print("  1. Could it have finished in fewer iterations? What caused the extras?")
print("  2. Set MAX_ITERATIONS = 3 and re-run. What does it return at the limit?")
