from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(50), nullable=False)

    plans = relationship("WorkoutPlan", back_populates="user")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)

    user = relationship("User", back_populates="plans")


Base.metadata.create_all(bind=engine)


# --- Storage Functions ---

def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str):
    db = SessionLocal()
    existing = db.query(User).filter(User.id == user_id).first()
    if existing:
        existing.name = name
        existing.age = age
        existing.weight = weight
        existing.goal = goal
        existing.intensity = intensity
    else:
        user = User(
            id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )
        db.add(user)
    db.commit()
    db.close()


def save_plan(user_id: int, plan: str):
    db = SessionLocal()
    workout = WorkoutPlan(user_id=user_id, original_plan=plan)
    db.add(workout)
    db.commit()
    db.close()


def update_plan(user_id: int, updated_text: str):
    db = SessionLocal()
    workout = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    if workout:
        workout.updated_plan = updated_text
        db.commit()
    db.close()


def get_original_plan(user_id: int):
    db = SessionLocal()
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
    db.close()
    return plan.original_plan if plan else None


def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user


def get_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users


def get_all_plans():
    db = SessionLocal()
    plans = db.query(WorkoutPlan).all()
    db.close()
    return plans