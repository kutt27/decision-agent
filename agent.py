import asyncio
import json
import os
from typing import Dict, Any, List

# Core configuration
API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = os.environ.get("ENDPOINT")
MODEL_NAME = "meta-llama/llama-3-70b-instruct" # Fast, high-reasoning open model

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
1. Deconstruct the user's situation using First Principles. Separating facts from emotional bias.
2. Cross-reference the choice against the User Profile Context. Does it feed an Anti-Goal?
3. Evaluate stress levels based on syntax, punctuation, and panic-driven statements.
4. Provide absolute, non-sugarcoated truth. Do not people-please."""

    async def analyze_decision(self, user_input: str, historical_context: List[str]) -> Dict[str, Any]:
        """Executes the decision-making loop asynchronously."""
        # In a real setup, you'd use a lightweight vector search here.
        # For Phase 1, we pass filtered text snippets.
        system_prompt = self._generate_system_prompt(historical_context)

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.2 # Kept low for structural reasoning
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # Simulated Asynchronous HTTP network call (Replace with actual httpx.AsyncClient post)
        try:
            await asyncio.sleep(0.5) # Network latency simulation

            # This is where your Autopsy tracking happens
            total_tokens = len(system_prompt.split()) + len(user_input.split())
            if total_tokens > 4000: # Setting an artificial small wall to test brittleness
                raise ValueError("ContextWindowExceeded: Simulated context saturation.")

            return {
                "status": "success",
                "decision_analysis": "Placeholder: Real LLM response would stream here."
            }

        except Exception as e:
            # Log the exact failure state for Phase 1 Autopsy
            failure = {
                "prompt_length": len(system_prompt),
                "error": str(e),
                "input_attempted": user_input
            }
            self.failure_log.append(failure)
            return {"status": "failed", "error": str(e)}
