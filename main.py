import asyncio
from agent import NorthStarAgent

# this will be os.file() from a static file.
# The foundational data structure defining who you are
MY_IDENTITY_CORE = {
    "values": ["Autonomy", "Deep technical mastery", "Physical vitality"],
    "vision": "Building foundational AI infrastructure from scratch, moving beyond wrapper frameworks.",
    "anti_goals": ["Trading time for status/titles", "Golden handcuffs (high pay, zero learning)", "Chronic burnout"]
}

async def main():
    # Initialize the agent with your core pillars
    agent = NorthStarAgent(user_profile=MY_IDENTITY_CORE)

    # Example Scenario: An emotional, potentially 'stupid' decision driven by FOMO or stress
    high_stress_input = "I'm feeling completely stuck at my current coding speed. This big enterprise company offered me a management role making 2x money. It's zero coding, all meetings, but the cash is insane and I feel like I'm falling behind my peers financially. Should I take it tonight?"

    print("🧠 Analyzing decision space against your personal North Star...")

    # Simple semantic context injection simulation
    relevant_past_notes = [
        "Note from Jan: I promised myself I would spend 2026 mastering JAX and systems engineering.",
        "Note from Mar: Corporate bureaucracy makes me want to pull my hair out."
    ]

    response = await agent.analyze_decision(high_stress_input, relevant_past_notes)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
