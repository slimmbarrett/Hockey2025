import os
import requests
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

BOT_TOKEN = os.getenv("7756073624:AAGAg-0Xmeq2Nb63vi7VkynRrwLynFqBetE")

@app.get("/broadcast")
def send_reminder():
    users = []  # Add user IDs manually or fetch from DB
    for user_id in users:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": user_id,
            "text": "🏒 Don't forget to make your hockey prediction today!"
        })
    return {"status": "done"}
