import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    prompt = f"""
You are a professional fitness trainer assistant.

Here's the original 7-day workout plan:
{original_plan}

User feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not revised.
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            if attempt < 2 and ("503" in str(e) or "RESOURCE_EXHAUSTED" in str(e)):
                time.sleep(2)
                continue
            return f"Error updating plan: {e}"