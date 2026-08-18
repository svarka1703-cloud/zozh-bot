from maxapi import Bot, Dispatcher, types
from keyboards.inline import back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def reports_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_reports":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(amount_ml), 0) FROM water_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        water = (await cursor.fetchone())[0]
        await cursor.close()
        
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(steps), 0) FROM steps_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        steps = (await cursor.fetchone())[0]
        await cursor.close()
        
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(calories), 0) FROM calorie_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        calories = (await cursor.fetchone())[0]
        await cursor.close()
        
        cursor = await db.conn.execute(
            "SELECT weight_kg FROM weight_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        weight_row = await cursor.fetchone()
        await cursor.close()
        weight = weight_row[0] if weight_row else "—"
        
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM workouts WHERE user_id = ? AND date(scheduled_at) = date('now')",
            (user_id,)
        )
        workouts = (await cursor.fetchone())[0]
        await cursor.close()
        
        water_pct = min(water / 2000 * 20, 20)
        steps_pct = min(steps / 10000 * 20, 20)
        cal_pct = min(calories / 2000 * 20, 20)
        
        text = "📊 Отчёт за сегодня\n\n"
        text += "💧 Вода\n"
        text += "🟦" * int(water_pct) + "⬜" * (20 - int(water_pct)) + "\n"
        text += f"{water} / 2000 мл\n\n"
        text += "👟 Шаги\n"
        text += "🟩" * int(steps_pct) + "⬜" * (20 - int(steps_pct)) + "\n"
        text += f"{steps} / 10000 шагов\n\n"
        text += "🔥 Калории\n"
        text += "🟥" * int(cal_pct) + "⬜" * (20 - int(cal_pct)) + "\n"
        text += f"{calories} / 2000 ккал\n\n"
        text += f"⚖️ Вес: {weight} кг\n"
        text += f"🏋️ Тренировок сегодня: {workouts}"
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )