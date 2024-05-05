import asyncio

import logging
import sys

from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from handlers.basic import send_dice
from handlers.git_issues import show_issues
from handlers.timer import set_timer, stop_timer, process_timer_selection

from keyboards.base_keyboard import get_base_keyboard
from keyboards.inline_for_timer import TIME_OPTIONS
from project_config import config

from utils.commands import set_commands


BOT_TOKEN = config.bot_token.get_secret_value()
ADMIN_ID = config.admin_id.get_secret_value()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.startup()
async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(chat_id=ADMIN_ID, text="I'm alive")


@dp.shutdown()
async def stop_bot():
    await bot.send_message(chat_id=ADMIN_ID, text="I'm done")


async def cmd_start(message: Message):
    await message.answer(f'Hello, {message.from_user.full_name} !',
                         reply_markup=get_base_keyboard())


async def main():
    dp.message.register(cmd_start, CommandStart())

    dp.message.register(show_issues,
                        F.text == 'Good first issues')
    dp.message.register(send_dice,
                        F.text == 'Dice')

    dp.message.register(set_timer,
                        F.text == 'Timer')
    dp.callback_query.register(
        process_timer_selection,
        lambda c: c.data in [str(option) for option in TIME_OPTIONS]
    )
    dp.message.register(stop_timer,
                        F.text == 'Stop timer')

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
