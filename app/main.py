from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(title="FitBuddy – AI Fitness Plan Generator")

# Mount static folder for CSS and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include all application routes
app.include_router(router)