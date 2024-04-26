import asyncio

import logging
import os
import sys

from aiogram import Dispatcher, Bot

from handlers.basic import send_dice
# from project_config import config

from dotenv import load_dotenv
load_dotenv()
# BOT_TOKEN = config.bot_token.get_secret_value()
# ADMIN_ID = config.admin_id.get_secret_value()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.startup()
async def start_bot():
    await bot.send_message(chat_id=ADMIN_ID, text="I'm alive")


@dp.shutdown()
async def stop_bot():
    await bot.send_message(chat_id=ADMIN_ID, text="I'm done")


async def main():
    dp.message.register(send_dice)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())