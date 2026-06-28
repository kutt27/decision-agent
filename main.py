"""
decision-agent — main.py
=========================
Interactive REPL that runs the decision agent in a multi-turn loop.

Usage:
  python main.py                    # Full interactive mode
  python main.py "Should I..."      # Single query, then interactive
"""

import sys

from agent import DecisionAgent

# ── Colours / formatting helpers ─────────────────────────────────────────


def blue(text: str) -> str:
    return f"\033[94m{text}\033[0m"


def green(text: str) -> str:
    return f"\033[92m{text}\033[0m"


def dim(text: str) -> str:
    return f"\033[2m{text}\033[0m"


def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


# ── Main ────────────────────────────────────────────────────────────────


def main():
    agent = DecisionAgent()

    # Optional: process a single query from CLI args
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n{blue('You:')} {query}\n")
        response = agent.process(query)
        print(f"{green('Agent:')}\n{response}\n")
        print(dim("─── Entering interactive mode ───\n"))

    print(bold("🧠 Decision Agent — interactive mode"))
    print(dim("Type your decision problem or question. Type 'exit' to quit.\n"))

    while True:
        try:
            user_input = input(f"{blue('You:')} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "/exit"):
            break

        response = agent.process(user_input)
        print(f"\n{green('Agent:')}\n{response}\n")


if __name__ == "__main__":
    main()
