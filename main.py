import asyncio
import logging
import os
import sys

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ai_assistants.handlers import ai_assistants
from core.handlers import basic, git_hub_issues, managing, timer, utilities

dotenv.load_dotenv()


BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
PROXY_API_TOKEN = os.environ.get('PROXY_API_TOKEN')


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=BOT_TOKEN)

    dp.include_router(utilities.router)
    dp.include_router(ai_assistants.router)
    dp.include_router(git_hub_issues.router)
    dp.include_router(basic.router)
    dp.include_router(timer.router)
    dp.include_router(managing.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
