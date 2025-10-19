from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import json
import os

app = FastAPI(title="Wellness Tracker API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage (in production, use a real database)
DATA_FILE = 'wellness_data.json'


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'mood_logs': [], 'sleep_logs': [], 'goals': [], 'breaks': []}


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# Models
class MoodLog(BaseModel):
    user_email: str
    date: str
    mood: str
    stress_level: int
    notes: Optional[str] = ""


class SleepLog(BaseModel):
    user_email: str
    date: str
    sleep_hours: float
    sleep_quality: str
    academic_performance: str
    notes: Optional[str] = ""


class Goal(BaseModel):
    user_email: str
    title: str
    description: str
    target_date: str
    status: str
    created_at: Optional[str] = None


class BreakReminder(BaseModel):
    user_email: str
    activity: str
    duration_minutes: int
    scheduled_time: str


# Mood/Stress Endpoints
@app.post("/api/mood")
async def create_mood_log(log: MoodLog):
    data = load_data()
    log_dict = log.dict()
    log_dict['id'] = len(data['mood_logs']) + 1
    log_dict['created_at'] = datetime.now().isoformat()
    data['mood_logs'].append(log_dict)
    save_data(data)
    return {"success": True, "log": log_dict}


@app.get("/api/mood")
async def get_mood_logs(user_email: str, limit: int = 30):
    data = load_data()
    user_logs = [log for log in data['mood_logs'] if log['user_email'] == user_email]
    return {"success": True, "logs": user_logs[-limit:]}


# Sleep Endpoints
@app.post("/api/sleep")
async def create_sleep_log(log: SleepLog):
    data = load_data()
    log_dict = log.dict()
    log_dict['id'] = len(data['sleep_logs']) + 1
    log_dict['created_at'] = datetime.now().isoformat()
    data['sleep_logs'].append(log_dict)
    save_data(data)
    return {"success": True, "log": log_dict}


@app.get("/api/sleep")
async def get_sleep_logs(user_email: str, limit: int = 30):
    data = load_data()
    user_logs = [log for log in data['sleep_logs'] if log['user_email'] == user_email]
    return {"success": True, "logs": user_logs[-limit:]}


# Goals Endpoints
@app.post("/api/goals")
async def create_goal(goal: Goal):
    data = load_data()
    goal_dict = goal.dict()
    goal_dict['id'] = len(data['goals']) + 1
    goal_dict['created_at'] = datetime.now().isoformat()
    data['goals'].append(goal_dict)
    save_data(data)
    return {"success": True, "goal": goal_dict}


@app.get("/api/goals")
async def get_goals(user_email: str):
    data = load_data()
    user_goals = [goal for goal in data['goals'] if goal['user_email'] == user_email]
    return {"success": True, "goals": user_goals}


@app.put("/api/goals/{goal_id}")
async def update_goal(goal_id: int, status: str, user_email: str):
    data = load_data()
    for goal in data['goals']:
        if goal['id'] == goal_id and goal['user_email'] == user_email:
            goal['status'] = status
            save_data(data)
            return {"success": True, "goal": goal}
    raise HTTPException(status_code=404, detail="Goal not found")


@app.delete("/api/goals/{goal_id}")
async def delete_goal(goal_id: int, user_email: str):
    data = load_data()
    data['goals'] = [g for g in data['goals'] if not (g['id'] == goal_id and g['user_email'] == user_email)]
    save_data(data)
    return {"success": True}


# Break Reminders Endpoints
@app.post("/api/breaks")
async def create_break(break_reminder: BreakReminder):
    data = load_data()
    break_dict = break_reminder.dict()
    break_dict['id'] = len(data['breaks']) + 1
    break_dict['created_at'] = datetime.now().isoformat()
    data['breaks'].append(break_dict)
    save_data(data)
    return {"success": True, "break": break_dict}


@app.get("/api/breaks")
async def get_breaks(user_email: str):
    data = load_data()
    user_breaks = [b for b in data['breaks'] if b['user_email'] == user_email]
    return {"success": True, "breaks": user_breaks}


@app.delete("/api/breaks/{break_id}")
async def delete_break(break_id: int, user_email: str):
    data = load_data()
    data['breaks'] = [b for b in data['breaks'] if not (b['id'] == break_id and b['user_email'] == user_email)]
    save_data(data)
    return {"success": True}


# Analytics
@app.get("/api/analytics")
async def get_analytics(user_email: str):
    data = load_data()

    mood_logs = [log for log in data['mood_logs'] if log['user_email'] == user_email]
    sleep_logs = [log for log in data['sleep_logs'] if log['user_email'] == user_email]
    goals = [goal for goal in data['goals'] if goal['user_email'] == user_email]

    avg_stress = sum(log['stress_level'] for log in mood_logs[-7:]) / len(mood_logs[-7:]) if mood_logs else 0
    avg_sleep = sum(log['sleep_hours'] for log in sleep_logs[-7:]) / len(sleep_logs[-7:]) if sleep_logs else 0

    goal_stats = {
        'total': len(goals),
        'completed': len([g for g in goals if g['status'] == 'completed']),
        'in_progress': len([g for g in goals if g['status'] == 'in_progress']),
        'pending': len([g for g in goals if g['status'] == 'pending'])
    }

    return {
        "success": True,
        "analytics": {
            "avg_stress_7days": round(avg_stress, 1),
            "avg_sleep_7days": round(avg_sleep, 1),
            "total_mood_logs": len(mood_logs),
            "total_sleep_logs": len(sleep_logs),
            "goal_stats": goal_stats
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)