from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=["start"])
async def start_message(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("Рассчитать"),
        KeyboardButton("Информация")
    ]
    kb.add(*buttons)
    await message.reply("Привет! Я бот, помогающий твоему здоровью.", reply_markup=kb)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(lambda message: message.text == "Рассчитать")
async def set_age(message: types.Message):
    await message.answer("Введите свой возраст.")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=int(message.text))
        await message.answer("Введите свой рост.")
        await UserState.growth.set()
    else:
        await message.answer("Пожалуйста, введите корректный возраст.")


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(growth=int(message.text))
        await message.answer("Введите свой вес.")
        await UserState.weight.set()
    else:
        await message.answer("Пожалуйста, введите корректный рост.")


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(weight=int(message.text))
        data = await state.get_data()
        age = data.get('age')
        growth = data.get('growth')
        weight = data.get('weight')
        bmr = 10 * weight + 6.25 * growth - 5 * age + 5
        await message.answer(f"Ваша норма калорий: {bmr:.2f}")
        await state.finish()
    else:
        await message.answer("Пожалуйста, введите корректный вес.")


@dp.message_handler()
async def all_message(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
