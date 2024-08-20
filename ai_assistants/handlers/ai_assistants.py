import logging
import os

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from openai import AsyncOpenAI, AuthenticationError, BadRequestError

import dotenv


dotenv.load_dotenv()


BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')
PROXY_API_TOKEN = os.environ.get('PROXY_API_TOKEN')

GPT_MODEL = 'gpt-4o'
DALLE_MODEL = 'dall-e-3'


client = AsyncOpenAI(api_key=PROXY_API_TOKEN,
                     base_url='https://api.proxyapi.ru/openai/v1')


router = Router()
bot = Bot(token=BOT_TOKEN)


class AIState(StatesGroup):
    gpt = State()
    dalle = State()


class Reference:
    def __init__(self):
        self.response = ''


reference = Reference()


@router.message(Command('chatgpt'))
async def enter_chatgpt_mode(message: types.Message, state: FSMContext):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer('This feature is only for the admin')
        return

    else:
        await message.answer('You are now in ChatGPT mode. '
                             'Send me a message, and I will reply '
                             'using ChatGPT. Send /cancel '
                             'to exit this mode.\n\n'
                             'Enter /clear_context to '
                             'start conversation over')
        await state.set_state(AIState.gpt)


@router.message(AIState.gpt, Command('cancel'))
async def leave_chatgpt_mode(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.clear()
    await message.answer('You have exited ChatGpt mode')


@router.message(AIState.gpt)
async def handle_chatgpt_message(message: types.Message):
    user_message = message.text

    try:
        response = await client.chat.completions.create(
            messages=[
                {'role': 'assistant', 'content': reference.response},
                {'role': 'user', 'content': user_message}
            ],
            model=GPT_MODEL,
        )
        logging.info(response)
        reference.response = response.choices[0].message.content
        await message.answer(reference.response, parse_mode='Markdown')

    except (AuthenticationError or BadRequestError or TelegramBadRequest):
        await message.answer('Something has gone wrong')


@router.message(AIState.gpt, Command('clear_context'))
async def clear_context(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Clearing the context %r', current_state)
    await clear_reference()
    await message.answer('The context has been successfully cleared')


@router.message(Command('dalle'))
async def enter_dalle_mode(message: types.Message, state: FSMContext):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer('This feature is only for the admin')
        return

    else:
        await message.answer('You are now in DALL-E mode. '
                             'Send me a message, and I will generate '
                             'a picture for you. Send /cancel '
                             'to exit this mode')
        await state.set_state(AIState.dalle)


@router.message(AIState.dalle, Command('cancel'))
async def leave_dalle_mode(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.clear()
    await message.answer('You have exited DALL-E mode')


@router.message(AIState.dalle)
async def handle_dalle_message(message: types.Message):
    await message.answer('It may take some time. Bare with me')
    user_message = message.text

    try:
        response = await client.images.generate(
            model=DALLE_MODEL,
            prompt=user_message,
            n=1,
            size='1024x1024'
        )
        logging.info(response)
        image_url = response.data[0].url
        photo = types.URLInputFile(image_url)
        await bot.send_photo(message.chat.id,
                             photo=photo,
                             caption='Here is your generated image')

    except (AuthenticationError or BadRequestError or TelegramBadRequest):
        await message.answer('Something has gone wrong')


async def clear_reference():
    reference.response = ''
