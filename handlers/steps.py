from maxapi import Bot, Dispatcher, types
from keyboards.inline import steps_menu_keyboard, back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def steps_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_steps":
        await callback.message.edit_text(
            "👟 Шаги\n\n"
            "Записывай свою активность. Цель — 10000 шагов в день.\n"
            "Выбери действие:",
            reply_markup=steps_menu_keyboard()
        )
    
    elif data == "steps_add":
        await callback.message.edit_text(
            "👟 Сколько шагов ты прошёл?\n"
            "Напиши число:",
            reply_markup=back_keyboard()
        )
    
    elif data == "steps_history":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(steps), 0) FROM steps_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        total = (await cursor.fetchone())[0]
        await cursor.close()
        
        cursor = await db.conn.execute(
            "SELECT steps, created_at FROM steps_logs WHERE user_id = ? AND date(created_at) = date('now') ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        logs = await cursor.fetchall()
        await cursor.close()
        
        text = f"👟 Шаги за сегодня: {total} из 10000\n\n"
        if logs:
            text += "Последние записи:\n"
            for steps, time in logs:
                text += f"• {steps} шагов — {time}\n"
        else:
            text += "Пока нет записей."
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )