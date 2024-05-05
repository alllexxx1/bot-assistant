from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_base_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text='Good first issues')
    keyboard_builder.button(text='Dice')
    keyboard_builder.button(text='Timer')
    keyboard_builder.button(text='Stop timer')

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder='Opt for an option'
    )
