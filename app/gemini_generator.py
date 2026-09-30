import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_workout_gemini(user_input: dict) -> str:
    prompt = f"""
You are a professional fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of **{user_input.get('goal')}**, and prefers **{user_input.get('intensity')}** intensity workouts.

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7)
"""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if attempt < 2 and ("503" in str(e) or "RESOURCE_EXHAUSTED" in str(e)):
                time.sleep(2)
                continue
            return f"Error: {e}"