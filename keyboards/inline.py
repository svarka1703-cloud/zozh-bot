def main_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "💧 Вода", "callback_data": "menu_water"},
                {"text": "👟 Шаги", "callback_data": "menu_steps"}
            ],
            [
                {"text": "🔥 Калории", "callback_data": "menu_calories"},
                {"text": "⚖️ Вес", "callback_data": "menu_weight"}
            ],
            [
                {"text": "🏋️ Тренировки", "callback_data": "menu_workouts"},
                {"text": "📊 Отчёты", "callback_data": "menu_reports"}
            ],
            [
                {"text": "⚙️ Настройки", "callback_data": "menu_settings"}
            ]
        ]
    }

def water_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "💧 +200 мл", "callback_data": "water_200"},
                {"text": "💧 +500 мл", "callback_data": "water_500"}
            ],
            [
                {"text": "💧 Свой объём", "callback_data": "water_custom"},
                {"text": "📊 История", "callback_data": "water_history"}
            ],
            [
                {"text": "🔙 Назад", "callback_data": "back_main"}
            ]
        ]
    }

def steps_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "👟 Добавить шаги", "callback_data": "steps_add"},
                {"text": "📊 История", "callback_data": "steps_history"}
            ],
            [
                {"text": "🔙 Назад", "callback_data": "back_main"}
            ]
        ]
    }

def calories_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🍳 Завтрак", "callback_data": "meal_breakfast"},
                {"text": "🍲 Обед", "callback_data": "meal_lunch"}
            ],
            [
                {"text": "🍝 Ужин", "callback_data": "meal_dinner"},
                {"text": "🍎 Перекус", "callback_data": "meal_snack"}
            ],
            [
                {"text": "📊 Дневная сводка", "callback_data": "calories_today"},
                {"text": "🔙 Назад", "callback_data": "back_main"}
            ]
        ]
    }

def weight_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "⚖️ Записать вес", "callback_data": "weight_add"},
                {"text": "📊 История", "callback_data": "weight_history"}
            ],
            [
                {"text": "🔙 Назад", "callback_data": "back_main"}
            ]
        ]
    }

def workouts_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🏋️ Добавить тренировку", "callback_data": "workout_add"},
                {"text": "📅 Календарь", "callback_data": "workout_calendar"}
            ],
            [
                {"text": "🔙 Назад", "callback_data": "back_main"}
            ]
        ]
    }

def back_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🔙 Назад", "callback_data": "back_main"}
            ]
        ]
    }

def workout_type_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🏃 Кардио", "callback_data": "workout_type_cardio"},
                {"text": "🏋️ Силовая", "callback_data": "workout_type_strength"}
            ],
            [
                {"text": "🧘 Йога", "callback_data": "workout_type_yoga"},
                {"text": "🚴 Велосипед", "callback_data": "workout_type_cycling"}
            ]
        ]
    }