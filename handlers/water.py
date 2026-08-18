from maxapi import Bot, Dispatcher, types
from keyboards.inline import water_menu_keyboard, back_keyboard, main_menu_keyboard
from database import db

dp = Dispatcher()

@dp.message_callback()
async def water_callbacks(callback: types.MessageCallback, bot: Bot):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "menu_water":
        await callback.message.edit_text(
            "💧 Вода\n\n"
            "Добавляй выпитую воду. Цель — 2000 мл в день.\n"
            "Выбери действие:",
            reply_markup=water_menu_keyboard()
        )
    
    elif data == "water_200":
        await db.conn.execute(
            "INSERT INTO water_logs (user_id, amount_ml) VALUES (?, 200)",
            (user_id,)
        )
        await db.conn.commit()
        await callback.answer("Добавлено 200 мл 💧")
        await callback.message.edit_text(
            "✅ 200 мл добавлено!\n\n"
            "💧 Вода\n"
            "Выбери действие:",
            reply_markup=water_menu_keyboard()
        )
    
    elif data == "water_500":
        await db.conn.execute(
            "INSERT INTO water_logs (user_id, amount_ml) VALUES (?, 500)",
            (user_id,)
        )
        await db.conn.commit()
        await callback.answer("Добавлено 500 мл 💧")
        await callback.message.edit_text(
            "✅ 500 мл добавлено!\n\n"
            "💧 Вода\n"
            "Выбери действие:",
            reply_markup=water_menu_keyboard()
        )
    
    elif data == "water_history":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(amount_ml), 0) FROM water_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        total = (await cursor.fetchone())[0]
        await cursor.close()
        
        cursor = await db.conn.execute(
            "SELECT amount_ml, created_at FROM water_logs WHERE user_id = ? AND date(created_at) = date('now') ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        logs = await cursor.fetchall()
        await cursor.close()
        
        text = f"💧 Вода за сегодня: {total} мл из 2000 мл\n\n"
        if logs:
            text += "Последние записи:\n"
            for amount, time in logs:
                text += f"• {amount} мл — {time}\n"
        else:
            text += "Пока нет записей."
        
        await callback.message.edit_text(text, reply_markup=back_keyboard())
    
    elif data == "back_main":
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )