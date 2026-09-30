def calculate_bmr(weight: float, age: int, gender: str = "general") -> float:
    """
    Estimates baseline daily caloric expenditure (BMR) using standard formulas.
    """
    # Baseline estimate: ~22 kcal per kg of body weight
    return round(weight * 22, 2)


def get_macronutrient_split(goal: str) -> dict:
    """
    Returns recommended macronutrient ratios based on the user's fitness goal.
    """
    goal_lower = goal.lower()
    if "loss" in goal_lower:
        return {"protein": "40%", "carbs": "30%", "fats": "30%"}
    elif "gain" in goal_lower or "muscle" in goal_lower:
        return {"protein": "30%", "carbs": "50%", "fats": "20%"}
    else:
        return {"protein": "25%", "carbs": "50%", "fats": "25%"}