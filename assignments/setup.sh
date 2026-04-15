#!/usr/bin/env bash
# Local setup for the Practical Track assignments.
# Mirrors what the Ona devcontainer does automatically.
set -euo pipefail

VENV=".venv"

echo "Setting up Practical Track assignments..."

# Create virtualenv if it doesn't exist
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
  echo "Created virtualenv at $VENV"
fi

# Activate
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# Install dependencies
pip install --quiet --upgrade pip
pip install --quiet openai tiktoken sentence-transformers fastapi uvicorn

echo "Dependencies installed."

# Start mock server if no real API key is set
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "No OPENAI_API_KEY found — starting mock server on port 8001..."
  export OPENAI_BASE_URL="http://localhost:8001/v1"
  export OPENAI_API_KEY="mock"
  uvicorn mock-server.main:app --port 8001 --log-level warning &
  MOCK_PID=$!
  sleep 1
  echo "Mock server running (PID $MOCK_PID)"
  echo ""
  echo "To use a real model:"
  echo "  export OPENAI_API_KEY=your-key-here && kill $MOCK_PID"
  echo "  Ona users: add the secret at https://app.gitpod.io/ai?user-settings=secrets"
  echo "  Docs: https://ona.com/docs/ona/configuration/secrets/user-secrets"
else
  echo "OPENAI_API_KEY detected — using real OpenAI API."
fi

echo ""
echo "Ready. Run any starter:"
echo "  python ch04-context-windows/starter.py"
echo "  python ch09-prompt-injection/starter.py"
echo "  python ch17-agent-loop/starter.py"
