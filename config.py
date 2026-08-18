import os
from dotenv import load_dotenv

load_dotenv()

MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "zozh_bot.db")
WATER_REMINDER_HOURS = int(os.getenv("WATER_REMINDER_HOURS", "2"))
STEPS_REMINDER_TIME = os.getenv("STEPS_REMINDER_TIME", "20:00")
WORKOUT_REMINDER_BEFORE_MIN = int(os.getenv("WORKOUT_REMINDER_BEFORE_MIN", "30"))  
