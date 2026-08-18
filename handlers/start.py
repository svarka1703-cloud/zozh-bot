from maxapi import Bot, Dispatcher, types
from keyboards.inline import main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_created()
async def cmd_start(message: types.Message, bot: Bot):
    if message.text == "/start":
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        await db.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.conn.commit()
        
        await db.conn.execute(
            "INSERT OR IGNORE INTO user_goals (user_id) VALUES (?)",
            (user_id,)
        )
        await db.conn.commit()
        
        await message.answer(
            "🤖 Привет! Я — ЗОЖник!\n\n"
            "Помогаю следить за здоровьем:\n"
            "💧 Вода — питьевой режим\n"
            "👟 Шаги — активность\n"
            "🔥 Калории — питание\n"
            "⚖️ Вес — динамика\n"
            "🏋️ Тренировки — календарь\n\n"
            "Выбери раздел:",
            reply_markup=main_menu_keyboard()
        )