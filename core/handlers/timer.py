import asyncio

from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from core.project_config import config

from core.keyboards.inline_for_timer import timer_keyboard


ACTIVE_USERS = set()

BOT_TOKEN = config.bot_token.get_secret_value()

bot = Bot(token=BOT_TOKEN)


async def set_timer(message: Message):
    await message.answer(text='Choose the timer duration',
                         reply_markup=timer_keyboard())


async def send_notification(bot: Bot, user_id: id, minutes: int):
    try:
        await asyncio.sleep(minutes * 60)

        if user_id in ACTIVE_USERS:
            await bot.send_message(
                chat_id=user_id,
                text='It is time to stretch your legs and take a little walk'
            )
            ACTIVE_USERS.remove(user_id)

    except asyncio.CancelledError:
        pass


async def process_timer_selection(callback_query: CallbackQuery):
    selected_time = int(callback_query.data)
    user_id = callback_query.from_user.id

    if user_id in ACTIVE_USERS:
        ACTIVE_USERS.remove(user_id)

    task = asyncio.create_task(send_notification(  # noqa: F841
        bot, user_id, selected_time
    ))
    ACTIVE_USERS.add(user_id)

    await callback_query.message.answer(
        f'Timer set to {selected_time} minutes'
    )


async def stop_timer(message: Message):
    user_id = message.from_user.id

    if user_id in ACTIVE_USERS:
        ACTIVE_USERS.remove(user_id)
        await message.answer(text='You have made your choice...')

    else:
        await message.answer(text='You have no timers set up yet')
