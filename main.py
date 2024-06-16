import asyncio

import logging
import os
import sys

from aiogram import Dispatcher, Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, URLInputFile

from openai import AsyncOpenAI, AuthenticationError, BadRequestError

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from core.handlers.basic import send_dice
from core.handlers.git_issues import show_issues
from core.handlers.timer import set_timer, stop_timer, process_timer_selection

from core.keyboards.base_keyboard import get_base_keyboard
from core.keyboards.inline_for_timer import TIME_OPTIONS
# from project_config import config

from core.utils.commands import set_commands

import dotenv


dotenv.load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

# BOT_TOKEN = config.bot_token.get_secret_value()
# ADMIN_ID = config.admin_id.get_secret_value()
# openai.api_key = config.openai_api_token.get_secret_value()

openai_api_key = os.environ.get('OPENAI_API_TOKEN')

GPT_MODEL = 'gpt-4o'
DALLE_MODEL = 'dall-e-3'

# client = AsyncOpenAI(api_key=openai_api_key)
client = AsyncOpenAI(api_key=openai_api_key,
                     base_url='https://api.proxyapi.ru/openai/v1')

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


# AI-assistants section
class AIState(StatesGroup):
    gpt = State()
    dalle = State()


class Reference:
    def __init__(self):
        self.response = ''


reference = Reference()


async def clear_past():
    reference.response = ''


@dp.message(Command('chatgpt'))
async def enter_chatgpt_mode(message: Message, state: FSMContext):
    if message.from_user.id != int(ADMIN_ID):
        await message.reply("This feature is only for the admin")
        return

    else:
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
            model=GPT_MODEL,
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
    await clear_past()
    await message.answer('The context successfully cleared.')


@dp.message(Command('dalle'))
async def enter_dalle_mode(message: Message, state: FSMContext):
    await state.set_state(AIState.dalle)
    await message.reply("You are now in DALL-E mode."
                        "Send me a message, and I'll generate"
                        "a picture for you. Send /cancel to exit this mode.")


@dp.message(Command('cancel'))
async def cancel_dalle_mode(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.reply("You have exited DALL-E mode.")


@dp.message(AIState.dalle)
async def handle_dalle_message(message: Message, state: FSMContext):
    await message.reply('It might take some time. Bare with me')
    user_message = message.text

    try:
        response = await client.images.generate(
            model=DALLE_MODEL,
            prompt=user_message,
            n=1,
            size='1024x1024'
        )
        image_url = response.data[0].url
        photo = URLInputFile(image_url)
        await bot.send_photo(message.chat.id,
                             photo=photo,
                             caption='Here is your generated image')

        # image_response = httpx.get(image_url)
        # image_path = 'generated_image.png'
        # with open(image_path, 'wb') as f:
        #     f.write(image_response.content)
        #
        # photo = FSInputFile(image_path)
        # await bot.send_photo(message.chat.id,
        #                      photo=photo,
        #                      caption='Here is your generated image')
        # os.remove(image_path)
        # await message.answer(response.data[0].url)

    except (AuthenticationError or BadRequestError or TelegramBadRequest):
        await message.answer("Something has gone wrong")


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
