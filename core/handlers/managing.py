import os

from aiogram import Bot, Router, types
from aiogram.filters import CommandStart

import dotenv

from core.keyboards.base_keyboard import get_base_keyboard
from core.utils.commands import set_commands


dotenv.load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')


bot = Bot(token=BOT_TOKEN)
router = Router()


@router.startup()
async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(chat_id=ADMIN_ID, text='I am alive')


@router.shutdown()
async def stop_bot():
    await bot.send_message(chat_id=ADMIN_ID, text='I am done')


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(f'Hello, {message.from_user.full_name} !',
                         reply_markup=get_base_keyboard())


@router.message()
async def handle_other_messages(message: types.Message):
    await message.answer('I have not got a slightest idea what '
                         'I am supposed to answer. Try something else')
