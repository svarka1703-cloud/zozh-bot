from maxapi import Bot, Dispatcher, types
from keyboards.inline import weight_menu_keyboard, back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def weight_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_weight":
        await callback.message.edit_text(
            "⚖️ Вес\n\n"
            "Записывай свой вес для отслеживания динамики.\n"
            "Выбери действие:",
            reply_markup=weight_menu_keyboard()
        )
    
    elif data == "weight_add":
        await callback.message.edit_text(
            "⚖️ Напиши свой вес в килограммах:\n"
            "Например: 70.5",
            reply_markup=back_keyboard()
        )
    
    elif data == "weight_history":
        cursor = await db.conn.execute(
            "SELECT weight_kg, created_at FROM weight_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 30",
            (user_id,)
        )
        logs = await cursor.fetchall()
        await cursor.close()
        
        if logs:
            current = logs[0][0]
            text = f"⚖️ Текущий вес: {current} кг\n\n"
            text += "История:\n"
            for weight, time in logs:
                text += f"• {weight} кг — {time}\n"
            
            if len(logs) > 1:
                diff = current - logs[-1][0]
                if diff < 0:
                    text += f"\n📉 За период: {abs(diff):.1f} кг"
                elif diff > 0:
                    text += f"\n📈 За период: +{diff:.1f} кг"
                else:
                    text += "\n➡️ За период: без изменений"
        else:
            text = "⚖️ Пока нет записей."
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )