from aiogram.enums import DiceEmoji
from aiogram.types import Message


async def send_dice(message: Message):
    await message.answer_dice(DiceEmoji.DICE)
