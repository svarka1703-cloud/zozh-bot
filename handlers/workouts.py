from maxapi import Bot, Dispatcher, types
from keyboards.inline import workouts_menu_keyboard, workout_type_keyboard, back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def workouts_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_workouts":
        await callback.message.edit_text(
            "🏋️ Тренировки\n\n"
            "Планируй занятия и получай напоминания.\n"
            "Выбери действие:",
            reply_markup=workouts_menu_keyboard()
        )
    
    elif data == "workout_add":
        await callback.message.edit_text(
            "🏋️ Какой тип тренировки?\n"
            "Выбери из списка:",
            reply_markup=workout_type_keyboard()
        )
    
    elif data.startswith("workout_type_"):
        type_map = {
            "workout_type_cardio": "🏃 Кардио",
            "workout_type_strength": "🏋️ Силовая",
            "workout_type_yoga": "🧘 Йога",
            "workout_type_cycling": "🚴 Велосипед"
        }
        workout_type = type_map.get(data, "Тренировка")
        
        await db.conn.execute(
            "INSERT INTO workouts (user_id, workout_type, scheduled_at) VALUES (?, ?, datetime('now'))",
            (user_id, workout_type)
        )
        await db.conn.commit()
        
        await callback.message.edit_text(
            f"✅ Тренировка добавлена: {workout_type}\n"
            f"📅 Дата: сегодня\n\n"
            "Тренировка запланирована!",
            reply_markup=back_keyboard()
        )
    
    elif data == "workout_calendar":
        cursor = await db.conn.execute(
            "SELECT workout_type, scheduled_at FROM workouts WHERE user_id = ? ORDER BY scheduled_at DESC LIMIT 14",
            (user_id,)
        )
        workouts = await cursor.fetchall()
        await cursor.close()
        
        if workouts:
            text = "📅 Твои тренировки:\n\n"
            for wtype, time in workouts:
                text += f"• {wtype} — {time}\n"
        else:
            text = "📅 Пока нет запланированных тренировок."
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )