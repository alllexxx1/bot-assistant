from aiogram.utils.keyboard import InlineKeyboardBuilder


TIME_OPTIONS = [30, 35, 40, 45, 50, 55]


def timer_keyboard():
    keyboard_builder = InlineKeyboardBuilder()

    for time_option in TIME_OPTIONS:
        keyboard_builder.button(text=str(time_option),
                                callback_data=str(time_option))

    keyboard_builder.adjust(3)
    return keyboard_builder.as_markup()
