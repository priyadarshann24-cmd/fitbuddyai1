from pydantic import BaseModel, Field

class WorkoutRequest(BaseModel):
    goal: str = Field(..., description="Fitness goal e.g., weight loss, muscle gain")
    intensity: str = Field(..., description="Workout intensity e.g., low, medium, high")

class UserInput(BaseModel):
    user_id: int
    name: str
    age: int
    weight: float
    goal: str
    intensity: str

class FeedbackRequest(BaseModel):
    user_id: int
    feedback: str