import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from openai import AsyncOpenAI, AuthenticationError, BadRequestError

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import dotenv

dotenv.load_dotenv()


BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

# openai.api_key = config.openai_api_token.get_secret_value()
openai_api_key = os.environ.get('OPENAI_API_TOKEN')
MODEL_NAME = 'gpt-4o'
# client = AsyncOpenAI(api_key=openai_api_key)
client = AsyncOpenAI(api_key=openai_api_key,
                     base_url='https://api.proxyapi.ru/openai/v1')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class AIState(StatesGroup):
    gpt = State()
    dalle = State()


class Reference:
    def __init__(self):
        self.response = ''


reference = Reference()


def clear_past():
    reference.response = ''


@dp.message(Command('chatgpt'))
async def enter_chatgpt_mode(message: Message, state: FSMContext):
    await state.set_state(AIState.gpt)
    await message.reply("You are now in ChatGPT mode."
                        "Send me a message, and I'll reply"
                        "using ChatGPT. Send /cancel to exit this mode.")


@dp.message(Command('cancel'))
async def cancel_chatgpt_mode(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.reply("You have exited ChatGPT mode.")


@dp.message(AIState.gpt)
async def handle_chatgpt_message(message: Message):
    user_message = message.text

    try:
        response = await client.chat.completions.create(
            messages=[
                {"role": "assistant", "content": reference.response},
                {"role": "user", "content": user_message}
            ],
            model=MODEL_NAME,
        )
        reference.response = response.choices[0].message.content
        await message.reply(reference.response, parse_mode='Markdown')

    except (AuthenticationError or BadRequestError or TelegramBadRequest):
        await message.reply("Something has gone wrong")


@dp.message(Command('clear'))
async def clear_context(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Clearing the context %r", current_state)
    clear_past()
    await message.answer('The context successfully cleared.')
