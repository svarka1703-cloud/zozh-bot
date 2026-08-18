from maxapi import Bot, Dispatcher, types
from keyboards.inline import calories_menu_keyboard, back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def calories_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_calories":
        await callback.message.edit_text(
            "🔥 Калории\n\n"
            "Записывай приёмы пищи. Цель — 2000 ккал в день.\n"
            "Выбери приём пищи:",
            reply_markup=calories_menu_keyboard()
        )
    
    elif data.startswith("meal_"):
        meal_map = {
            "meal_breakfast": "🍳 Завтрак",
            "meal_lunch": "🍲 Обед",
            "meal_dinner": "🍝 Ужин",
            "meal_snack": "🍎 Перекус"
        }
        meal = meal_map.get(data, "Приём пищи")
        await callback.message.edit_text(
            f"{meal}\n\n"
            "Напиши описание и калории в формате:\n"
            "Например: Овсянка 250",
            reply_markup=back_keyboard()
        )
    
    elif data == "calories_today":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(calories), 0) FROM calorie_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        total = (await cursor.fetchone())[0]
        await cursor.close()
        
        cursor = await db.conn.execute(
            "SELECT meal_type, description, calories, created_at FROM calorie_logs WHERE user_id = ? AND date(created_at) = date('now') ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        )
        logs = await cursor.fetchall()
        await cursor.close()
        
        text = f"🔥 Калории за сегодня: {total} из 2000\n\n"
        if logs:
            text += "Последние записи:\n"
            for meal, desc, cal, time in logs:
                text += f"• {meal}: {desc} — {cal} ккал ({time})\n"
        else:
            text += "Пока нет записей."
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )