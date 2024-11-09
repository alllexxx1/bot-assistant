import asyncio
import os

import dotenv
from aiogram import Bot, F, Router, types

from core.keyboards import inline_for_timer

dotenv.load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

ACTIVE_USERS = set()

router = Router()
bot = Bot(token=BOT_TOKEN)


@router.message(F.text == 'Timer')
async def set_timer(message: types.Message):
    await message.answer(
        text='Choose the timer duration',
        reply_markup=inline_for_timer.timer_keyboard(),
    )


@router.callback_query(
    lambda c: c.data
    in [str(option) for option in inline_for_timer.TIME_OPTIONS]
)
async def process_timer_selection(callback_query: types.CallbackQuery):
    selected_time = int(callback_query.data)
    user_id = callback_query.from_user.id

    ACTIVE_USERS.add(user_id)
    asyncio.create_task(send_notification(bot, user_id, selected_time))

    await callback_query.message.answer(
        f'Timer set to {selected_time} minutes'
    )


@router.message(F.text == 'Stop timer')
async def stop_timer(message: types.Message):
    user_id = message.from_user.id

    if user_id in ACTIVE_USERS:
        ACTIVE_USERS.remove(user_id)
        await message.answer(text='You have made your choice...')

    else:
        await message.answer(text='You have no timers set up yet')


async def send_notification(bot: Bot, user_id: id, minutes: int):
    try:
        await asyncio.sleep(minutes * 60)

        if user_id in ACTIVE_USERS:
            await bot.send_message(
                chat_id=user_id,
                text='It is time to stretch your legs and take a little walk',
            )
            ACTIVE_USERS.remove(user_id)

    except asyncio.CancelledError:
        pass
