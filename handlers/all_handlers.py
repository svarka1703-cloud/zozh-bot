from maxapi import Bot, Dispatcher, types
from maxapi.types.attachments.attachment import AttachmentType
from database import db

dp = Dispatcher()

user_states = {}

def build_keyboard(buttons):
    keyboard_buttons = []
    for row in buttons:
        row_buttons = []
        for text, payload in row:
            row_buttons.append(types.CallbackButton(text=text, payload=payload))
        keyboard_buttons.append(row_buttons)
    payload = types.ButtonsPayload(buttons=keyboard_buttons)
    attachment = types.Attachment(type=AttachmentType.INLINE_KEYBOARD, payload=payload)
    return [attachment]

def calculate_targets(gender, weight, height, age, activity, goal):
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multipliers = {
        "low": 1.2,
        "medium": 1.375,
        "high": 1.55,
        "very_high": 1.725
    }
    multiplier = activity_multipliers.get(activity, 1.2)
    
    daily_calories = bmr * multiplier
    
    if goal == "lose":
        daily_calories *= 0.85
    elif goal == "gain":
        daily_calories *= 1.15
    
    water_ml = weight * 30
    if activity in ["high", "very_high"]:
        water_ml += 500
    
    return int(water_ml), int(daily_calories)

def get_main_menu_keyboard():
    return build_keyboard([
        [("Вода", "menu_water"), ("Шаги", "menu_steps")],
        [("Калории", "menu_calories"), ("Вес", "menu_weight")],
        [("Тренировки", "menu_workouts"), ("Отчёт", "menu_reports")],
        [("Настройки", "menu_settings")]
    ])

def get_settings_keyboard():
    return build_keyboard([
        [("Цель воды", "settings_water")],
        [("Цель шагов", "settings_steps")],
        [("Цель калорий", "settings_calories")],
        [("Напоминания", "settings_reminders")],
        [("Назад", "back_main")]
    ])

def get_reminders_keyboard():
    return build_keyboard([
        [("Каждый час", "remind_1h")],
        [("Каждые 2 часа", "remind_2h")],
        [("Каждые 3 часа", "remind_3h")],
        [("Отключить", "remind_off")],
        [("Назад", "menu_settings")]
    ])

@dp.bot_started()
async def handle_bot_started(event):
    await event.send(
        "👋 Привет! Я — твой персональный ЗОЖник!\n\n"
        "Помогу рассчитать норму воды и калорий,\n"
        "а также следить за прогрессом.\n\n"
        "Нажми кнопку ниже, чтобы заполнить анкету!",
        attachments=build_keyboard([[("Старт", "start_survey")]])
    )

@dp.message_created()
async def handle_messages(message: types.MessageCreated):
    text = ""
    if message.message and message.message.body:
        text = message.message.body.text or ""
    
    user_id = message.from_user.user_id
    
    await db.conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, message.from_user.username or "Unknown")
    )
    await db.conn.commit()
    
    await db.conn.execute(
        "INSERT OR IGNORE INTO user_goals (user_id) VALUES (?)",
        (user_id,)
    )
    await db.conn.commit()
    
    state = user_states.get(user_id, {})
    
    if state.get("stage") == "awaiting_gender":
        if text.lower() in ["муж", "мужской", "м", "male"]:
            state["gender"] = "male"
            state["stage"] = "awaiting_age"
            user_states[user_id] = state
            await message.send("Сколько тебе лет? Напиши число:")
        elif text.lower() in ["жен", "женский", "ж", "female"]:
            state["gender"] = "female"
            state["stage"] = "awaiting_age"
            user_states[user_id] = state
            await message.send("Сколько тебе лет? Напиши число:")
        else:
            await message.send(
                "Выбери пол:",
                attachments=build_keyboard([[("Мужской", "gender_male"), ("Женский", "gender_female")]])
            )
    
    elif state.get("stage") == "awaiting_age":
        if text.isdigit() and 10 <= int(text) <= 100:
            state["age"] = int(text)
            state["stage"] = "awaiting_weight"
            user_states[user_id] = state
            await message.send("Какой у тебя вес в кг? Напиши число (например: 70):")
        else:
            await message.send("Введи возраст цифрой (от 10 до 100):")
    
    elif state.get("stage") == "awaiting_weight":
        if text.replace(".", "").isdigit() and 30 <= float(text) <= 300:
            state["weight"] = float(text)
            state["stage"] = "awaiting_height"
            user_states[user_id] = state
            await message.send("Какой у тебя рост в см? Напиши число (например: 175):")
        else:
            await message.send("Введи вес в кг (от 30 до 300):")
    
    elif state.get("stage") == "awaiting_height":
        if text.isdigit() and 100 <= int(text) <= 250:
            state["height"] = int(text)
            state["stage"] = "awaiting_activity"
            user_states[user_id] = state
            await message.send(
                "Какой у тебя уровень активности?",
                attachments=build_keyboard([
                    [("Низкая", "activity_low")],
                    [("Средняя", "activity_medium")],
                    [("Высокая", "activity_high")],
                    [("Очень высокая", "activity_very_high")]
                ])
            )
        else:
            await message.send("Введи рост в см (от 100 до 250):")
    
    elif state.get("stage") == "awaiting_water_setting":
        if text.isdigit() and 500 <= int(text) <= 10000:
            await db.conn.execute(
                "UPDATE user_goals SET water_goal_ml = ? WHERE user_id = ?",
                (int(text), user_id)
            )
            await db.conn.commit()
            user_states.pop(user_id, None)
            await message.send(
                f"✅ Новая цель по воде: {text} мл в день.",
                attachments=get_settings_keyboard()
            )
        else:
            await message.send("Введи объём в мл (от 500 до 10000):")
    
    elif state.get("stage") == "awaiting_steps_setting":
        if text.isdigit() and 1000 <= int(text) <= 50000:
            await db.conn.execute(
                "UPDATE user_goals SET steps_goal = ? WHERE user_id = ?",
                (int(text), user_id)
            )
            await db.conn.commit()
            user_states.pop(user_id, None)
            await message.send(
                f"✅ Новая цель по шагам: {text} шагов в день.",
                attachments=get_settings_keyboard()
            )
        else:
            await message.send("Введи количество шагов (от 1000 до 50000):")
    
    elif state.get("stage") == "awaiting_calories_setting":
        if text.isdigit() and 800 <= int(text) <= 10000:
            await db.conn.execute(
                "UPDATE user_goals SET calorie_goal = ? WHERE user_id = ?",
                (int(text), user_id)
            )
            await db.conn.commit()
            user_states.pop(user_id, None)
            await message.send(
                f"✅ Новая цель по калориям: {text} ккал в день.",
                attachments=get_settings_keyboard()
            )
        else:
            await message.send("Введи количество калорий (от 800 до 10000):")
    
    elif text == "/start" or text == "start":
        await message.send(
            "Давай заполним анкету!\n"
            "Выбери пол:",
            attachments=build_keyboard([[("Мужской", "gender_male"), ("Женский", "gender_female")]])
        )
        user_states[user_id] = {"stage": "awaiting_gender"}
    
    elif text == "+200":
        await db.conn.execute("INSERT INTO water_logs (user_id, amount_ml) VALUES (?, 200)", (user_id,))
        await db.conn.commit()
        await message.send("✅ 200 мл добавлено!")
    
    elif text == "+500":
        await db.conn.execute("INSERT INTO water_logs (user_id, amount_ml) VALUES (?, 500)", (user_id,))
        await db.conn.commit()
        await message.send("✅ 500 мл добавлено!")
    
    elif text.isdigit() and int(text) > 0 and int(text) < 100000 and not state:
        steps = int(text)
        await db.conn.execute("INSERT INTO steps_logs (user_id, steps) VALUES (?, ?)", (user_id, steps))
        await db.conn.commit()
        await message.send(f"✅ Записано: {steps} шагов!")
    
    elif text.replace(".", "").isdigit() and "." in text and not state:
        weight = float(text)
        await db.conn.execute("INSERT INTO weight_logs (user_id, weight_kg) VALUES (?, ?)", (user_id, weight))
        await db.conn.commit()
        await message.send(f"✅ Вес записан: {weight} кг")

@dp.message_callback()
async def handle_callbacks(callback: types.MessageCallback):
    data = callback.callback.payload if callback.callback else ""
    user_id = callback.from_user.user_id
    
    if data == "start_survey":
        await callback.message.send(
            "Давай заполним анкету!\n"
            "Выбери пол:",
            attachments=build_keyboard([[("Мужской", "gender_male"), ("Женский", "gender_female")]])
        )
        user_states[user_id] = {"stage": "awaiting_gender"}
    
    elif data in ["gender_male", "gender_female"]:
        state = user_states.get(user_id, {})
        state["gender"] = "male" if data == "gender_male" else "female"
        state["stage"] = "awaiting_age"
        user_states[user_id] = state
        await callback.message.send("Сколько тебе лет? Напиши число:")
    
    elif data.startswith("activity_"):
        activity_map = {
            "activity_low": "low",
            "activity_medium": "medium",
            "activity_high": "high",
            "activity_very_high": "very_high"
        }
        state = user_states.get(user_id, {})
        state["activity"] = activity_map.get(data, "medium")
        state["stage"] = "awaiting_goal"
        user_states[user_id] = state
        await callback.message.send(
            "Какая у тебя цель?",
            attachments=build_keyboard([
                [("Похудение", "goal_lose")],
                [("Набор массы", "goal_gain")],
                [("Быть в тонусе", "goal_maintain")]
            ])
        )
    
    elif data.startswith("goal_"):
        goal_map = {
            "goal_lose": "lose",
            "goal_gain": "gain",
            "goal_maintain": "maintain"
        }
        state = user_states.get(user_id, {})
        state["goal"] = goal_map.get(data, "maintain")
        user_states[user_id] = state
        
        water_goal, calorie_goal = calculate_targets(
            state.get("gender", "male"),
            state.get("weight", 70),
            state.get("height", 170),
            state.get("age", 25),
            state.get("activity", "medium"),
            state.get("goal", "maintain")
        )
        
        steps_goal = 10000
        if state.get("activity") == "low":
            steps_goal = 7000
        elif state.get("activity") == "high":
            steps_goal = 12000
        elif state.get("activity") == "very_high":
            steps_goal = 15000
        
        await db.conn.execute(
            "UPDATE user_goals SET water_goal_ml = ?, calorie_goal = ?, steps_goal = ? WHERE user_id = ?",
            (water_goal, calorie_goal, steps_goal, user_id)
        )
        await db.conn.commit()
        
        user_states.pop(user_id, None)
        
        await callback.message.send(
            "🎉 Анкета заполнена!\n\n"
            f"📊 Твои персональные нормы:\n"
            f"💧 Вода: {water_goal} мл в день\n"
            f"🔥 Калории: {calorie_goal} ккал в день\n"
            f"👟 Шаги: {steps_goal} шагов в день\n\n"
            "Ты можешь изменить нормы в Настройках."
        )
        
        await callback.message.send("Главное меню:", attachments=get_main_menu_keyboard())
    
    elif data == "menu_water":
        cursor = await db.conn.execute("SELECT water_goal_ml FROM user_goals WHERE user_id = ?", (user_id,))
        water_goal = (await cursor.fetchone())[0]
        await cursor.close()
        await callback.message.send(
            f"💧 Вода\n\nТвоя цель: {water_goal} мл в день.\nНапиши +200 или +500:",
            attachments=build_keyboard([
                [("+200 мл", "water_200"), ("+500 мл", "water_500")],
                [("📊 История", "water_history")],
                [("🔙 Назад", "back_main")]
            ])
        )
    
    elif data == "water_200":
        await db.conn.execute("INSERT INTO water_logs (user_id, amount_ml) VALUES (?, 200)", (user_id,))
        await db.conn.commit()
        await callback.message.send("✅ 200 мл добавлено!")
    
    elif data == "water_500":
        await db.conn.execute("INSERT INTO water_logs (user_id, amount_ml) VALUES (?, 500)", (user_id,))
        await db.conn.commit()
        await callback.message.send("✅ 500 мл добавлено!")
    
    elif data == "water_history":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(amount_ml), 0) FROM water_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        total = (await cursor.fetchone())[0]
        await cursor.close()
        cursor = await db.conn.execute("SELECT water_goal_ml FROM user_goals WHERE user_id = ?", (user_id,))
        water_goal = (await cursor.fetchone())[0]
        await cursor.close()
        await callback.message.send(
            f"💧 Вода за сегодня: {total} мл из {water_goal} мл",
            attachments=build_keyboard([[("🔙 Назад", "back_main")]])
        )
    
    elif data == "menu_steps":
        cursor = await db.conn.execute("SELECT steps_goal FROM user_goals WHERE user_id = ?", (user_id,))
        steps_goal = (await cursor.fetchone())[0]
        await cursor.close()
        await callback.message.send(
            f"👟 Шаги\n\nТвоя цель: {steps_goal} шагов.\nНапиши число шагов:",
            attachments=build_keyboard([
                [("📊 История", "steps_history")],
                [("🔙 Назад", "back_main")]
            ])
        )
    
    elif data == "steps_history":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(steps), 0) FROM steps_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        total = (await cursor.fetchone())[0]
        await cursor.close()
        cursor = await db.conn.execute("SELECT steps_goal FROM user_goals WHERE user_id = ?", (user_id,))
        steps_goal = (await cursor.fetchone())[0]
        await cursor.close()
        await callback.message.send(
            f"👟 Шаги за сегодня: {total} из {steps_goal}",
            attachments=build_keyboard([[("🔙 Назад", "back_main")]])
        )
    
    elif data == "menu_calories":
        cursor = await db.conn.execute("SELECT calorie_goal FROM user_goals WHERE user_id = ?", (user_id,))
        calorie_goal = (await cursor.fetchone())[0]
        await cursor.close()
        await callback.message.send(
            f"🔥 Калории\n\nТвоя цель: {calorie_goal} ккал в день.\n\n"
            "Напиши в формате: Завтрак Овсянка 250",
            attachments=build_keyboard([
                [("📊 Сводка", "calories_today")],
                [("🔙 Назад", "back_main")]
            ])
        )
    
    elif data == "calories_today":
        cursor = await db.conn.execute(
            "SELECT COALESCE(SUM(calories), 0) FROM calorie_logs WHERE user_id = ? AND date(created_at) = date('now')",
            (user_id,)
        )
        total = (await cursor.fetchone())[0]
        await cursor.close()
        cursor = await db.conn.execute("SELECT calorie_goal FROM user_goals WHERE user_id = ?", (user_id,))
        calorie_goal = (await cursor.fetchone())[0]
        await cursor.close()
        await callback.message.send(
            f"🔥 Калории за сегодня: {total} из {calorie_goal}",
            attachments=build_keyboard([[("🔙 Назад", "back_main")]])
        )
    
    elif data == "menu_water":
        pass
    
    elif data == "menu_weight":
        await callback.message.send(
            "⚖️ Вес\n\nНапиши вес в кг (например: 70.5):",
            attachments=build_keyboard([
                [("📊 История", "weight_history")],
                [("🔙 Назад", "back_main")]
            ])
        )
    
    elif data == "weight_history":
        cursor = await db.conn.execute(
            "SELECT weight_kg, created_at FROM weight_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        logs = await cursor.fetchall()
        await cursor.close()
        if logs:
            text_out = "⚖️ История веса:\n\n"
            for weight, time in logs:
                text_out += f"• {weight} кг — {time}\n"
        else:
            text_out = "⚖️ Пока нет записей."
        await callback.message.send(text_out, attachments=build_keyboard([[("🔙 Назад", "back_main")]]))
    
    elif data == "menu_workouts":
        await callback.message.send(
            "🏋️ Тренировки\n\nНапиши тип: Кардио, Силовая, Йога, Велосипед",
            attachments=build_keyboard([
                [("📅 Календарь", "workout_calendar")],
                [("🔙 Назад", "back_main")]
            ])
        )
    
    elif data == "workout_calendar":
        cursor = await db.conn.execute(
            "SELECT workout_type, scheduled_at FROM workouts WHERE user_id = ? ORDER BY scheduled_at DESC LIMIT 14",
            (user_id,)
        )
        workouts = await cursor.fetchall()
        await cursor.close()
        if workouts:
            text_out = "📅 Тренировки:\n\n"
            for wtype, time in workouts:
                text_out += f"• {wtype} — {time}\n"
        else:
            text_out = "📅 Пока нет тренировок."
        await callback.message.send(text_out, attachments=build_keyboard([[("🔙 Назад", "back_main")]]))
    
    elif data == "menu_reports":
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
        
        cursor = await db.conn.execute("SELECT water_goal_ml, steps_goal, calorie_goal FROM user_goals WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()
        water_goal, steps_goal, calorie_goal = row if row else (2000, 10000, 2000)
        
        text_out = "📊 Отчёт за сегодня\n\n"
        text_out += f"💧 Вода: {water} / {water_goal} мл\n"
        text_out += f"👟 Шаги: {steps} / {steps_goal}\n"
        text_out += f"🔥 Калории: {calories} / {calorie_goal}"
        
        await callback.message.send(text_out, attachments=build_keyboard([[("🔙 Назад", "back_main")]]))
    
    elif data == "menu_settings":
        await callback.message.send(
            "⚙️ Настройки\n\n"
            "Здесь ты можешь изменить свои цели:",
            attachments=get_settings_keyboard()
        )
    
    elif data == "settings_water":
        cursor = await db.conn.execute("SELECT water_goal_ml FROM user_goals WHERE user_id = ?", (user_id,))
        water_goal = (await cursor.fetchone())[0]
        await cursor.close()
        user_states[user_id] = {"stage": "awaiting_water_setting"}
        await callback.message.send(
            f"💧 Текущая цель по воде: {water_goal} мл.\n"
            "Напиши новый объём в мл (от 500 до 10000):"
        )
    
    elif data == "settings_steps":
        cursor = await db.conn.execute("SELECT steps_goal FROM user_goals WHERE user_id = ?", (user_id,))
        steps_goal = (await cursor.fetchone())[0]
        await cursor.close()
        user_states[user_id] = {"stage": "awaiting_steps_setting"}
        await callback.message.send(
            f"👟 Текущая цель по шагам: {steps_goal} шагов.\n"
            "Напиши новое количество (от 1000 до 50000):"
        )
    
    elif data == "settings_calories":
        cursor = await db.conn.execute("SELECT calorie_goal FROM user_goals WHERE user_id = ?", (user_id,))
        calorie_goal = (await cursor.fetchone())[0]
        await cursor.close()
        user_states[user_id] = {"stage": "awaiting_calories_setting"}
        await callback.message.send(
            f"🔥 Текущая цель по калориям: {calorie_goal} ккал.\n"
            "Напиши новое количество (от 800 до 10000):"
        )
    
    elif data == "settings_reminders":
        await callback.message.send(
            "🔔 Настройка напоминаний о воде:\n\n"
            "Выбери интервал:",
            attachments=get_reminders_keyboard()
        )
    
    elif data == "remind_1h":
        await db.conn.execute("UPDATE user_goals SET reminder_hours = 1 WHERE user_id = ?", (user_id,))
        await db.conn.commit()
        await callback.message.send(
            "✅ Напоминания о воде: каждый час",
            attachments=get_settings_keyboard()
        )
    
    elif data == "remind_2h":
        await db.conn.execute("UPDATE user_goals SET reminder_hours = 2 WHERE user_id = ?", (user_id,))
        await db.conn.commit()
        await callback.message.send(
            "✅ Напоминания о воде: каждые 2 часа",
            attachments=get_settings_keyboard()
        )
    
    elif data == "remind_3h":
        await db.conn.execute("UPDATE user_goals SET reminder_hours = 3 WHERE user_id = ?", (user_id,))
        await db.conn.commit()
        await callback.message.send(
            "✅ Напоминания о воде: каждые 3 часа",
            attachments=get_settings_keyboard()
        )
    
    elif data == "remind_off":
        await db.conn.execute("UPDATE user_goals SET reminder_hours = 0 WHERE user_id = ?", (user_id,))
        await db.conn.commit()
        await callback.message.send(
            "🔕 Напоминания о воде отключены",
            attachments=get_settings_keyboard()
        )
    
    elif data == "back_main":
        await callback.message.send("Главное меню:", attachments=get_main_menu_keyboard())