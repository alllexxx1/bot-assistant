import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from functools import reduce


router = Router()


UTILITIES = [60.149, 38.415, 548.13, 287.12, 644.57]
COEFFICIENTS = [50.93, 202.79, 8.23, 2.62, 5.66]
LATEST_COST = 2500.00


class Utilities(StatesGroup):
    utilities = State()


@router.message(F.text == 'Utilities')
async def set_meters_values(message: types.Message, state: FSMContext):
    await message.answer('Hello, drop your figures here in '
                         'the following format: \n\n'
                         '65.857\n40.407\n645.53\n318.76\n810.72\n\n'
                         'Enter /cancel to roll back')

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

        if len(utilities) != 5:
            await message.answer('Take a close look at an example format')

        else:
            total_cost = count_utilities(utilities)
            await message.answer('New utilities are saved. \n'
                                 'To check them, type '
                                 '<b>Current utilities</b>',
                                 parse_mode='HTML')
            await message.answer(f'Here is the cost: <b>{total_cost}</b>',
                                 parse_mode='HTML')
            await state.clear()

    except ValueError:
        await message.answer('Incorrect format. Try one more time')


@router.message(F.text == 'Current utilities')
async def get_current_utilities(message: types.Message):
    await message.answer(text=str(UTILITIES)[1:-1])


@router.message(F.text == 'Last cost')
async def get_latest_cost(message: types.Message):
    cost = str(round(LATEST_COST, 2))
    await message.answer(text=f'<b>{cost}</b>', parse_mode='HTML') \
        if LATEST_COST \
        else await message.answer(text='Nothing')


def count_utilities(new_utilities):
    global UTILITIES
    global LATEST_COST

    difference = [new_utilities[i] - UTILITIES[i]
                  for i in range(len(new_utilities))]

    utility_expenses = [difference[j] * COEFFICIENTS[j]
                        for j in range(len(difference))]

    total_cost = reduce(lambda x, y: x + y, utility_expenses)
    LATEST_COST = total_cost

    UTILITIES = new_utilities

    return str(round(total_cost, 2))
