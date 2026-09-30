import os
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas import UserInput, FeedbackRequest, WorkoutRequest
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan
from app.database import (
    SessionLocal,
    User,
    WorkoutPlan,
    save_user,
    save_plan,
    update_plan,
    get_original_plan,
    get_user,
    get_all_users,
    get_all_plans,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

router = APIRouter()

# -------------------------------------------------------------
# Web Interface Routes
# -------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
def home_route(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_html(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    save_user(
        user_id=user_id,
        name=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity
    )

    plan = generate_workout_gemini({
        "goal": goal,
        "intensity": intensity
    })
    nutrition_tip = generate_nutrition_tip_with_flash(goal)
    save_plan(user_id=user_id, plan=plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": username,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": plan,
            "nutrition_tip": nutrition_tip
        }
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_html(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...)
):
    original_plan = get_original_plan(user_id)
    if not original_plan:
        raise HTTPException(status_code=404, detail="Original plan not found for this user.")

    updated_plan_text = update_workout_plan(original_plan=original_plan, user_feedback=feedback)
    update_plan(user_id=user_id, updated_text=updated_plan_text)

    user = get_user(user_id)
    username = user.name if user else "User"
    goal = user.goal if user else "general fitness"
    age = user.age if user else 25
    weight = user.weight if user else 70.0
    intensity = user.intensity if user else "medium"

    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": username,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": updated_plan_text,
            "original_plan": original_plan,
            "nutrition_tip": nutrition_tip,
            "feedback_applied": True
        }
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users_html(request: Request):
    users = get_all_users()
    all_plans = {plan.user_id: plan for plan in get_all_plans()}

    user_data = []
    for user in users:
        plan = all_plans.get(user.id)
        user_data.append({
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "original_plan": plan.original_plan if plan else "N/A",
            "updated_plan": plan.updated_plan if (plan and plan.updated_plan) else "Not updated"
        })

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": user_data}
    )


@router.post("/delete-user/{user_id}")
def delete_user_route(user_id: int):
    db = SessionLocal()
    db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).delete()
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    db.close()
    return RedirectResponse(url="/view-all-users", status_code=303)


# -------------------------------------------------------------
# JSON API Routes
# -------------------------------------------------------------

@router.post("/generate-workout/gemini")
async def generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini({"goal": request.goal, "intensity": request.intensity})
        return {"model": "gemini-pro", "workout_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nutrition-tip")
def get_flash_tip(goal: str):
    tip = generate_nutrition_tip_with_flash(goal)
    return {"goal": goal, "nutrition_tip": tip}


@router.post("/generate-plan")
def generate_plan_api(user_data: UserInput):
    try:
        save_user(
            user_id=user_data.user_id,
            name=user_data.name,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity
        )
        plan = generate_workout_gemini({"goal": user_data.goal, "intensity": user_data.intensity})
        save_plan(user_data.user_id, plan)
        return {"message": "Workout plan generated and saved successfully!", "workout_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


@router.post("/update-plan/{user_id}")
def update_user_plan_api(user_id: int, data: FeedbackRequest):
    original = get_original_plan(user_id)
    if not original:
        return {"error": "Original plan not found for this user."}
    updated = update_workout_plan(original, data.feedback)
    update_plan(user_id, updated)
    return {"updated_plan": updated}