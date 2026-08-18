from maxapi import Bot, Dispatcher, types
from keyboards.inline import back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def settings_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_settings":
        cursor = await db.conn.execute(
            "SELECT water_goal_ml, steps_goal, calorie_goal FROM user_goals WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        
        if row:
            water_goal, steps_goal, calorie_goal = row
            text = "⚙️ Твои цели:\n\n"
            text += f"💧 Вода: {water_goal} мл\n"
            text += f"👟 Шаги: {steps_goal} шагов\n"
            text += f"🔥 Калории: {calorie_goal} ккал\n\n"
            text += "Настройки пока в разработке. Скоро сможешь менять цели!"
        else:
            text = "⚙️ Цели не установлены. Напиши /start"
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )