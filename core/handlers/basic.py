from aiogram import enums, F, Router, types


router = Router()


@router.message(F.text == 'Dice')
async def send_dice(message: types.Message):
    await message.answer_dice(enums.DiceEmoji.DICE)
