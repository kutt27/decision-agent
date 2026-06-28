"""
decision-agent — agent.py
===========================
The core DecisionAgent class.

Architecture:
  profile.yaml  ──►  static identity (values, vision, anti-goals)
  brain/brain.md  ──►  persistent "journal" the model reads & rewrites each cycle

Flow per user message:
  1. Build prompt = system instructions + profile + brain + recent history + user input
  2. Call model (sync httpx) with a cheap open-weight model
  3. Parse response into [TO_USER] message + [BRAIN_UPDATE] brain content
  4. Save updated brain, append to conversation history, return message
"""

import os
import re
from pathlib import Path
from typing import Optional

import httpx
import yaml

# Auto-load .env file if it exists (no dependency on manual sourcing)
_env_path = Path(".env")
if _env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(_env_path)
    except ImportError:
        pass  # python-dotenv not installed, user must source .env manually

# ── Configuration ────────────────────────────────────────────────────────

API_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
API_URL = os.environ.get(
    "ENDPOINT",
    "https://openrouter.ai/api/v1/chat/completions",
)

# Default: cheap, fast, capable reasoning model available on OpenRouter.
# Override via env var MODEL_NAME if desired.
MODEL_NAME = os.environ.get("MODEL_NAME", "google/gemini-3.5-flash")

# ── Helpers ──────────────────────────────────────────────────────────────


def _extract_tag(text: str, tag: str) -> Optional[str]:
    """Extract content between [TAG] and [/TAG] markers, case-insensitive."""
    pattern = re.compile(
        rf"\[{tag}\](.*?)\[/{tag}\]", re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _load_yaml(path: str) -> dict:
    """Load a YAML file, returning an empty dict if missing."""
    if not os.path.isfile(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def _load_text(path: str) -> str:
    """Load a text file, returning empty string if missing."""
    if not os.path.isfile(path):
        return ""
    with open(path, "r") as f:
        return f.read()


def _save_text(path: str, content: str) -> None:
    """Write text content to a file, creating parent dirs as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ── Agent ────────────────────────────────────────────────────────────────


class DecisionAgent:
    """A persistent decision partner with a writable 'brain' journal."""

    def __init__(
        self,
        profile_path: str = "profile.yaml",
        brain_path: str = "brain/brain.md",
        max_history: int = 6,
    ):
        self.profile = _load_yaml(profile_path)
        self.brain_path = brain_path
        self.brain = _load_text(brain_path)
        self.max_history = max_history
        self.conversation: list[dict[str, str]] = []

    # ── Public API ───────────────────────────────────────────────────

    def process(self, user_input: str) -> str:
        """Process one user message: build prompt → call model → parse → persist.

        Returns the agent's message to the user (the [TO_USER] section).
        Side-effect: updates brain/brain.md and appends to conversation history.
        """
        prompt = self._build_prompt(user_input)
        try:
            raw_output = self._call_model(prompt)
        except Exception as e:
            msg = f"⚠️ {e}"
            self.conversation.append({"role": "user", "content": user_input})
            self.conversation.append({"role": "assistant", "content": msg})
            return msg

        message = self._parse_and_persist(raw_output)

        self.conversation.append({"role": "user", "content": user_input})
        self.conversation.append({"role": "assistant", "content": message})

        return message

    # ── Prompt construction ──────────────────────────────────────────

    def _build_prompt(self, user_input: str) -> list[dict[str, str]]:
        """Build the message list for the chat-completion API."""

        profile_str = yaml.dump(self.profile, default_flow_style=False).strip()

        # Recent conversation (most recent first, reversed for chronological)
        recent = self.conversation[-self.max_history * 2 :]

        system_text = f"""You are a Decision Agent — a hyper-rational, human-centered thinking partner.

You have a **brain** (brain.md) that stores your distilled wisdom across conversations. Read it before every response to recall past patterns and lessons.

=== YOUR IDENTITY (profile.yaml) ===
{profile_str}

=== YOUR BRAIN (brain.md) ===
{self.brain}

=== HOW TO INTERACT ===
1. **First pass** — Ask 1-2 clarifying questions to surface the real decision beneath the surface.
2. **Analysis** — When you have enough context, give a structured analysis:
   - First-principles deconstruction: separate concrete facts from emotional bias
   - Cross-reference against profile: does this choice feed an anti-goal or align with a core value?
   - Stress/urgency evaluation: is the user in a panic state? Address it directly.
   - Cognitive bias check: check for sunk cost, availability, anchoring, framing, status quo, confirmation bias
3. **The user may challenge your analysis.** Go deeper each cycle. Treat each challenge as signal, not resistance.
4. **Always end with a question** (to clarify) or a **verdict** (if you have enough signal).

=== OUTPUT FORMAT ===
You MUST respond with EXACTLY two tagged sections:

[TO_USER]
Your message to the user here — questions, analysis, recommendations, or all of the above.
[/TO_USER]

[BRAIN_UPDATE]
Updated brain.md content. Integrate new insights from this interaction into existing knowledge.
Keep it CONCISE. Compress and refine. Remove redundancies. Preserve critical patterns and lessons.
[/BRAIN_UPDATE]

Remember: raw truth, not people-pleasing. Do not optimise for validation."""

        messages = [{"role": "system", "content": system_text}]

        for msg in recent:
            messages.append(msg)

        messages.append({"role": "user", "content": user_input})

        return messages

    # ── Model call ───────────────────────────────────────────────────

    def _call_model(self, messages: list[dict[str, str]]) -> str:
        """Sync call to an OpenRouter-compatible chat endpoint."""
        if not API_KEY:
            raise RuntimeError(
                "No API key found. Set OPENROUTER_API_KEY or OPENROUTER_KEY "
                "in your .env file or environment."
            )

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.3,  # Low for structural reasoning
            "max_tokens": 4096,
        }

        with httpx.Client(timeout=45.0) as client:
            response = client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    # ── Response parsing & persistence ───────────────────────────────

    def _parse_and_persist(self, raw: str) -> str:
        """Extract [TO_USER] and [BRAIN_UPDATE] from the model output.

        Falls back gracefully if tags are missing.
        """
        message = _extract_tag(raw, "TO_USER")
        brain_update = _extract_tag(raw, "BRAIN_UPDATE")

        if message is None:
            # Model didn't use tags — treat whole output as message
            message = raw.strip()

        if brain_update:
            self.brain = brain_update
            _save_text(self.brain_path, brain_update)

        return message
