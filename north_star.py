import asyncio
import json
import os
import httpx
from typing import Dict, Any, List

# Core configuration
API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = os.environ.get("ENDPOINT")

# We'll use a strong open-weight reasoning model available on OpenRouter
MODEL_NAME = "google/gemini-2.5-pro"

class NorthStarAgent:
    def __init__(self, user_profile: Dict[str, Any]):
        self.user_profile = user_profile
        self.failure_log: List[Dict[str, Any]] = []

    def _generate_system_prompt(self, context_snippets: List[str]) -> str:
        """Grounds the agent in the user's specific identity architecture."""
        return f"""You are the user's Personal North Star, a hyper-rational, human-centered decision architect.
Your core directive is to keep the user on their straight path, preventing impulsive, stupid, or fear-based choices.

USER PROFILE CONTEXT:
- Core Values: {', '.join(self.user_profile.get('values', []))}
- Long-term Vision: {self.user_profile.get('vision', '')}
- Anti-Goals (What to avoid): {', '.join(self.user_profile.get('anti_goals', []))}

RELEVANT MEMORIES/CONTEXT:
{chr(10).join(f"- {s}" for s in context_snippets)}

DECISION FRAMEWORK:
1. Deconstruct the user's situation using First Principles. Separate concrete facts from emotional bias.
2. Cross-reference the choice against the User Profile Context. Does it feed or lean into an Anti-Goal?
3. Evaluate the user's anxiety/stress level based on their punctuation and text syntax. Address it directly.
4. Provide raw, non-sugarcoated truth. Do not people-please or optimize for validation."""

    async def analyze_decision(self, user_input: str, historical_context: List[str]) -> Dict[str, Any]:
        """Executes the decision-making loop over OpenRouter."""
        system_prompt = self._generate_system_prompt(historical_context)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-username/phase1-northstar", # Optional metadata for OpenRouter
            "X-Title": "North Star Agent"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.2  # Kept low for high logical consistency
        }

        async with httpx.AsyncClient() as client:
            try:
                # Set a strict timeout to watch for network/model bottlenecks (Brittle Agent metric)
                response = await client.post(API_URL, headers=headers, json=payload, timeout=30.0)

                # Check for HTTP Errors
                response.raise_for_status()

                result = response.json()
                analysis = result['choices'][0]['message']['content']

                return {
                    "status": "success",
                    "analysis": analysis
                }

            except Exception as e:
                # Capture the failure state for the Autopsy report
                failure_state = {
                    "input_attempted": user_input,
                    "error_class": e.__class__.__name__,
                    "error_message": str(e)
                }
                self.failure_log.append(failure_state)
                return {
                    "status": "failed",
                    "error": str(e)
                }

# --- APPLICATION EXECUTION ---
MY_IDENTITY_CORE = {
    "values": ["Autonomy", "Deep technical mastery", "Physical vitality"],
    "vision": "Building foundational AI infrastructure from scratch, moving beyond wrapper frameworks.",
    "anti_goals": ["Trading time for status/titles", "Golden handcuffs (high pay, zero learning)", "Chronic burnout"]
}

async def main():
    agent = NorthStarAgent(user_profile=MY_IDENTITY_CORE)

    # Context injected from historical notes
    relevant_past_notes = [
        "Note from Jan: I promised myself I would spend 2026 mastering JAX and systems engineering.",
        "Note from Mar: Corporate bureaucracy makes me feel creatively drained."
    ]

    # Emotional Scenario Input
    high_stress_input = (
        "I'm feeling completely stuck at my current coding speed. This big enterprise company "
        "just offered me a management role making 2x money. It's zero coding, all meetings and syncs, "
        "but the cash is insane and I feel like I'm falling behind my peers financially. Should I take it tonight?!"
    )

    print("🧠 Querying OpenRouter endpoint...")
    result = await agent.analyze_decision(high_stress_input, relevant_past_notes)

    print("\n--- AGENT RESPONSE ---")
    if result["status"] == "success":
        print(result["analysis"])
    else:
        print(f"❌ Execution Faulted: {result['error']}")
        print(f"📋 System Failure Log: {json.dumps(agent.failure_log, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
