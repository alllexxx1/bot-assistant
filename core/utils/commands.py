from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Start the bot'),
        BotCommand(command='chatgpt', description='Enter the СhatGpt mode'),
        BotCommand(command='dalle', description='Enter the Dall-E mode'),
        BotCommand(command='cancel', description='Exit current mode'),
        BotCommand(
            command='clear_context', description='Clear ChatGpt context'
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
