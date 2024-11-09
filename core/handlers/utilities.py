import logging
from functools import reduce

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()


UTILITIES = [79.400, 48.621, 5.5394, 757.64, 371.35, 961.22]
COEFFICIENTS = [59.80, 234.56, 2803.24, 8.94, 3.02, 6.15]
LATEST_COST = 2500.00


class Utilities(StatesGroup):
    utilities = State()


@router.message(F.text == 'Utilities')
async def set_meters_values(message: types.Message, state: FSMContext):
    await message.answer(
        'Hello, drop your figures here in '
        'the following format: \n\n'
        '65.857\n40.407\n5.5394\n645.53\n318.76\n810.72\n\n'
        'Enter /cancel to roll back'
    )

    await state.set_state(Utilities.utilities)


@router.message(Utilities.utilities, Command('cancel'))
async def leave_utilities_mode(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer('You have exited utilities mode')


@router.message(Utilities.utilities)
async def get_utilities(message: types.Message, state: FSMContext):
    try:
        utilities = list(map(float, message.text.split()))

        if len(utilities) != 6:
            await message.answer('Take a close look at an example format')

        else:
            total_cost = count_utilities(utilities)
            await message.answer(
                'New utilities are saved. \n'
                'To check them, type '
                '<b>Current utilities</b>',
                parse_mode='HTML',
            )
            await message.answer(
                f'Here is the cost: <b>{total_cost}</b>', parse_mode='HTML'
            )
            await state.clear()

    except ValueError:
        await message.answer('Incorrect format. Try one more time')


@router.message(F.text == 'Current utilities')
async def get_current_utilities(message: types.Message):
    current_utilities = (
        f'ХВ - {UTILITIES[0]}\n'
        f'ГВ - {UTILITIES[1]}\n'
        f'О - {UTILITIES[2]}\n\n'
        f'Т1 - {UTILITIES[3]}\n'
        f'Т2 - {UTILITIES[4]}\n'
        f'Т3 - {UTILITIES[5]}\n'
    )
    await message.answer(current_utilities)


@router.message(F.text == 'Last cost')
async def get_latest_cost(message: types.Message):
    cost = str(round(LATEST_COST, 2))
    (
        await message.answer(text=f'<b>{cost}</b>', parse_mode='HTML')
        if LATEST_COST
        else await message.answer(text='Nothing')
    )


def count_utilities(new_utilities):
    global UTILITIES
    global LATEST_COST

    difference = [
        new_utilities[i] - UTILITIES[i] for i in range(len(new_utilities))
    ]

    utility_expenses = [
        difference[j] * COEFFICIENTS[j] for j in range(len(difference))
    ]

    total_cost = reduce(lambda x, y: x + y, utility_expenses)
    LATEST_COST = total_cost

    UTILITIES = new_utilities

    return str(round(total_cost, 2))
