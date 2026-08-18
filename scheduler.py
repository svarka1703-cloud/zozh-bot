import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import db

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
bot_instance = None

async def check_all_reminders():
    if not bot_instance:
        return
    try:
        cursor = await db.conn.execute("SELECT DISTINCT user_id FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        
        current_hour = None
        from datetime import datetime
        current_hour = datetime.now().hour
        
        for (user_id,) in users:
            try:
                cursor = await db.conn.execute(
                    "SELECT water_goal_ml, reminder_hours FROM user_goals WHERE user_id = ?",
                    (user_id,)
                )
                row = await cursor.fetchone()
                await cursor.close()
                
                if row:
                    water_goal, reminder_hours = row
                else:
                    water_goal, reminder_hours = 2000, 2
                
                if reminder_hours and reminder_hours > 0:
                    if current_hour % reminder_hours == 0:
                        await send_water_reminder(user_id, water_goal)
            except Exception as e:
                logger.error(f"Ошибка проверки напоминаний для {user_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка в check_all_reminders: {e}")

async def send_water_reminder(user_id, water_goal):
    try:
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(amount_ml), 0) FROM water_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        water_today = (await cursor.fetchone())[0]
        await cursor.close()
        
        remaining = water_goal - water_today
        
        if remaining > 0:
            glasses = int(remaining / 250) + (1 if remaining % 250 > 0 else 0)
            
            await bot_instance.send_message(
                user_id,
                f"💧 Напоминание!\n\n"
                f"Ты выпил: {water_today} мл\n"
                f"Цель: {water_goal} мл\n"
                f"Осталось: {remaining} мл ({glasses} стаканов)\n\n"
                f"Напиши +200 или +500 чтобы записать воду."
            )
        else:
            await bot_instance.send_message(
                user_id,
                "🎉 Отлично! Ты выполнил норму воды на сегодня!"
            )
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания {user_id}: {e}")

def setup_scheduler(bot):
    global bot_instance
    bot_instance = bot
    
    # Проверяем напоминания каждый час
    scheduler.add_job(
        check_all_reminders,
        CronTrigger(minute=0),
        id="water_reminder_check",
        replace_existing=True
    )

def start_scheduler():
    scheduler.start()
    logger.info("Планировщик запущен")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("Планировщик остановлен")