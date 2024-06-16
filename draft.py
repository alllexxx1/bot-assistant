import openai
import os
import dotenv

dotenv.load_dotenv()

# Playing around with OpenAI API
api_key = os.environ.get('OPENAI_API_TOKEN')
client = openai.OpenAI(api_key=api_key,
                       base_url='https://api.proxyapi.ru/openai/v1')  # client for getting access to API through ProxyAPI
# client = openai.OpenAI(api_key=openai_api_key)  # client for direct API

# ChatGPT API request
# response = client.chat.completions.create(
#     model="gpt-3.5-turbo", messages=[{"role": "user", "content": "How are you?"}]
# )
#
# print(response.choices[0].message.content)


# DALL-E API request
# picture = client.images.generate(
#         model='dall-e-3',
#         prompt='cat and DOG',
#         n=1,
#         size='1024x1024'
# )
#
# print(picture.data[0].url)





# Handler that sends a picture
# @dp.message(F.text.casefold() == 'generate')
# async def send_picture(message: Message):
#         image_path = 'generated_image.png'
#         photo = URLInputFile('https://upload.wikimedia.org/wikipedia/commons/7/78/Image.jpg')
#         # photo = FSInputFile(image_path)
#         await message.answer_photo(photo=photo, caption='Here is your generated image')





# Integration ChatGPT and DALL-E (logic and handlers)

# import asyncio
#
# import logging
# import os
# import sys
#
# from aiogram import Dispatcher, Bot, F, Router
# from aiogram.exceptions import TelegramBadRequest
# from aiogram.filters import CommandStart, Command
# from aiogram.types import Message, InputFile, FSInputFile, URLInputFile
#
# from openai import AsyncOpenAI, AuthenticationError, BadRequestError
#
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
#
#
# from core.handlers.basic import send_dice
# from core.handlers.git_issues import show_issues
# from core.handlers.timer import set_timer, stop_timer, process_timer_selection
#
# from core.keyboards.base_keyboard import get_base_keyboard
# from core.keyboards.inline_for_timer import TIME_OPTIONS
# class AIState(StatesGroup):
#     gpt = State()
#     dalle = State()
#
#
# class Reference:
#     def __init__(self):
#         self.response = ''
#
# reference = Reference()
#
#
# def clear_past():
#     reference.response = ''
#
#
# @dp.message(Command('chatgpt'))
# async def enter_chatgpt_mode(message: Message, state: FSMContext):
#     await state.set_state(AIState.gpt)
#     await message.reply("You are now in ChatGPT mode. Send me a message, and I'll reply using ChatGPT. Send /cancel to exit this mode.")
#
#
# @dp.message(Command('cancel'))
# async def cancel_chatgpt_mode(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     logging.info("Cancelling state %r", current_state)
#     await state.clear()
#     await message.reply("You have exited ChatGPT mode.")
#
#
# @dp.message(AIState.gpt)
# async def handle_chatgpt_message(message: Message):
#     user_message = message.text
#
#     try:
#         response = await client.chat.completions.create(
#             messages=[
#                 {"role": "assistant", "content": reference.response},
#                 {"role": "user", "content": user_message}
#             ],
#             model=MODEL_NAME,
#         )
#         reference.response = response.choices[0].message.content
#         await message.reply(reference.response, parse_mode='Markdown')
#
#     except (AuthenticationError or BadRequestError or TelegramBadRequest):
#         await message.reply("Something has gone wrong")
#
#
# @dp.message(Command('clear'))
# async def clear_context(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     logging.info("Clearing the context %r", current_state)
#     clear_past()
#     await message.answer('The context successfully cleared.')
#
#
# @dp.message(Command('dalle'))
# async def enter_dalle_mode(message: Message, state: FSMContext):
#     await state.set_state(AIState.dalle)
#     await message.reply("You are now in DALL-E mode. Send me a message, and I'll generate a picture for you. Send /cancel to exit this mode.")
#
#
# @dp.message(Command('cancel'))
# async def cancel_dalle_mode(message: Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     logging.info("Cancelling state %r", current_state)
#     await state.clear()
#     await message.reply("You have exited DALL-E mode.")
#
#
# @dp.message(AIState.dalle)
# async def handle_dalle_message(message: Message, state: FSMContext):
#     await message.reply('It might take some time. Bare with me')
#     user_message = message.text
#
#     try:
#         response = await client.images.generate(
#             model='dall-e-3',
#             prompt=user_message,
#             n=1,
#             size='1024x1024'
#         )
#         image_url = response.data[0].url
#         photo = URLInputFile(image_url)
#         await bot.send_photo(message.chat.id, photo=photo, caption='Here is your generated image')
#
#         # image_response = httpx.get(image_url)
#         # image_path = 'generated_image.png'
#         # with open(image_path, 'wb') as f:
#         #     f.write(image_response.content)
#         #
#         # photo = FSInputFile(image_path)
#         # await bot.send_photo(message.chat.id, photo=photo, caption='Here is your generated image')
#         # os.remove(image_path)
#         # await message.answer(response.data[0].url)
#
#     except (AuthenticationError or BadRequestError or TelegramBadRequest):
#         await message.answer("Something has gone wrong")
