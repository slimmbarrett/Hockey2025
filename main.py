from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к PostgreSQL (Supabase)
conn = psycopg2.connect(os.getenv("SUPABASE_DB_URL"))
cursor = conn.cursor()

# Telegram Bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Модель для прогноза
class Prediction(BaseModel):
    userId: str
    name: str
    matchId: int
    scoreA: int
    scoreB: int

@app.get("/next_match")
def get_next_match():
    cursor.execute("""
        SELECT * FROM matches
        WHERE result IS NULL AND date >= CURRENT_DATE
        ORDER BY date ASC LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        return {
            "id": row[0],
            "teamA": row[1],
            "teamB": row[2],
            "date": row[3].isoformat(),
            "result": row[4]
        }
    return {"message": "No upcoming matches"}

@app.post("/submit_prediction")
def submit_prediction(p: Prediction):
    cursor.execute("""
        INSERT INTO users (user_id, name)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (p.userId, p.name))

    cursor.execute("""
        INSERT INTO predictions (user_id, match_id, score_a, score_b)
        VALUES (%s, %s, %s, %s)
    """, (p.userId, p.matchId, p.scoreA, p.scoreB))

    conn.commit()
    return {"message": "Prediction submitted"}

@app.get("/leaderboard")
def get_leaderboard():
    cursor.execute("SELECT user_id, name, points FROM users ORDER BY points DESC")
    rows = cursor.fetchall()
    return [{"userId": r[0], "name": r[1], "points": r[2]} for r in rows]

@app.get("/calculate_points")
def calculate_points():
    cursor.execute("""
        SELECT p.user_id, p.match_id, p.score_a, p.score_b, m.result
        FROM predictions p
        JOIN matches m ON p.match_id = m.id
        WHERE m.result IS NOT NULL
    """)
    rows = cursor.fetchall()

    updated = {}

    for r in rows:
        user_id, match_id, score_a, score_b, result = r
        result_data = json.loads(result) if isinstance(result, str) else result
        correct_score = score_a == result_data["scoreA"] and score_b == result_data["scoreB"]
        correct_outcome = (
            (score_a - score_b) * (result_data["scoreA"] - result_data["scoreB"]) > 0
            or (score_a == score_b and result_data["scoreA"] == result_data["scoreB"])
        )
        points = 3 if correct_score else 1 if correct_outcome else 0
        updated[user_id] = updated.get(user_id, 0) + points

    for user_id, pts in updated.items():
        cursor.execute("UPDATE users SET points = points + %s WHERE user_id = %s", (pts, user_id))

    conn.commit()
    return {"message": "Points calculated"}

@app.get("/notify")
def notify_all_users():
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()

    for (user_id,) in rows:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": user_id,
                "text": "🏒 Сегодня матч! Успей сделать прогноз в Telegram WebApp!"
            }
        )
    return {"message": "Notifications sent"}
