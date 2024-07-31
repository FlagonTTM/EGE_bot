from aiogram.filters import Command
from aiogram.enums import ParseMode
from keyboard import *
import asyncio
import logging
import json
from random import randint
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
import stress
from aiogram.fsm.state import State, StatesGroup
from config import *
from inf_test import *
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Form(StatesGroup):
    phys = State()
    math = State()
class ReminderStates(StatesGroup):
    waiting_for_hours = State()

reminders = {}

@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    await message.answer_photo(photo='https://i.postimg.cc/MpMsmyqv/2024-08-01-005634116.png', reply_markup=menu)
    await message.answer(f'Привет {message.from_user.first_name}\nЭто твой помощник с подготовкой к ЕГЭ,'
                         f' чтобы точно получить высокие баллы поставь напоминание или не забывай регулярно заходить!',
                         reply_markup=start.as_markup())

@dp.message(F.text.lower() == "меню")
async def with_puree(message: types.Message):
    await message.answer_photo(
        photo='https://i.postimg.cc/MpMsmyqv/2024-08-01-005634116.png')
    await message.answer(f'Привет {message.from_user.first_name}\nЭто твой помощник с подготовкой к ЕГЭ,'
                         f' чтобы точно получить высокие баллы поставь напоминание или не забывай регулярно заходить!',
                         reply_markup=start.as_markup())


user_data = {}

@dp.callback_query(lambda callback_query: callback_query.data.startswith('subject_'))
async def process_subject_callback(callback_query: types.CallbackQuery, state: FSMContext):
    subject = callback_query.data.split('_')[1]
    if subject == 'informatics':
        user_data[callback_query.from_user.id] = 0  # Начинаем с первого вопроса
        await send_quiz_inf(callback_query.message.chat.id, callback_query.from_user.id)
    elif subject == 'physics':
        await callback_query.message.answer('Чтобы начать заниматься, выберите раздел физики выбрав одну из кнопок ниже', reply_markup=start_phys.as_markup())
    elif subject == 'russian':
        await send_random_quiz(callback_query.from_user.id)
    elif subject == 'math':
        await callback_query.message.answer('Для подготовки к математике выбери задание, к которому ты будешь готовиться', reply_markup=start_math.as_markup())
    elif subject == 'napom':
        await callback_query.message.answer("Через сколько часов тебе нужно напоминание?(Напиши только число)")
        await state.set_state(ReminderStates.waiting_for_hours)
    await callback_query.answer()

#НАПОМИНАНИЕ
@dp.message(ReminderStates.waiting_for_hours)
async def process_hours(message: Message, state: FSMContext):
    try:
        hours = int(message.text)
        await state.update_data(hours=hours)
        declension = get_hour_declension(hours)
        await message.answer(f"Напомню через {hours} {declension}!")
        await state.clear()

        reminder_task = asyncio.create_task(schedule_reminder(message.chat.id, hours))
        reminders[message.chat.id] = reminder_task
    except ValueError:
        await message.answer("Пожалуйста, введи число.(В часах)")

async def schedule_reminder(chat_id: int, hours: int):
    await asyncio.sleep(hours * 3600)
    try:
        await bot.send_message(chat_id, "Время напоминания пришло!")
    except:
        None

@dp.message(F.text.lower() == "отменить напоминание")
async def cancel_reminder(message: Message):
    if message.chat.id in reminders:
        reminders[message.chat.id].cancel()
        del reminders[message.chat.id]
        await message.answer("Ваше напоминание отменено.")
    else:
        await message.answer("У вас нет активных напоминаний.")

#ФИЗИКА

@dp.callback_query(lambda callback_query: callback_query.data.startswith('phys_'))
async def process_phys_callback(callback_query: types.CallbackQuery, state: FSMContext):
    phys = callback_query.data.split('_')[1]
    await callback_query.answer()

    if phys == "mechanics":
        keyboard = InlineKeyboardBuilder().add(
            InlineKeyboardButton(text="Динамика", callback_data="dinamics"),
            InlineKeyboardButton(text="Кинематика", callback_data="kinematics"),
            InlineKeyboardButton(text="Статика", callback_data="statics"),
            InlineKeyboardButton(text="Законы сохранения", callback_data="conservation_laws")
        ).adjust(2)
        await callback_query.message.edit_text(
            text="Выберите подраздел механики!",
            reply_markup=keyboard.as_markup()
        )
    elif phys == "electrodynamics":
        keyboard = InlineKeyboardBuilder().add(
            InlineKeyboardButton(text="Колебательный контур", callback_data="oscillating_circuit"),
            InlineKeyboardButton(text="Постоянный ток", callback_data="direct_current"),
            InlineKeyboardButton(text="Магнитное поле", callback_data="magnetic_field")
        ).adjust(2)
        await callback_query.message.edit_text(
            text="Выберите подраздел электродинамики!",
            reply_markup=keyboard.as_markup()
        )
    elif phys == "thermodynamics":
        keyboard = InlineKeyboardBuilder().add(
            InlineKeyboardButton(text="Идеальный газ", callback_data="ideal_gas"),
            InlineKeyboardButton(text="Фазовые переходы", callback_data="phase_transitions")
        ).adjust(2)
        await callback_query.message.edit_text(
            text="Выберите подраздел термодинамики!",
            reply_markup=keyboard.as_markup()
        )
    elif phys == "Molecular Physics":
        keyboard = InlineKeyboardBuilder().add(
            InlineKeyboardButton(text="Молекулы", callback_data="molecules"),
            InlineKeyboardButton(text="Основное уравнение МКТ", callback_data="MKT")
        ).adjust(2)
        await callback_query.message.edit_text(
            text="Выберите подраздел Молекулярной физики!",
            reply_markup=keyboard.as_markup()
        )

@dp.callback_query(lambda c: c.data in [
    "dinamics", "kinematics", "statics", "conservation_laws",
    "oscillating_circuit", "direct_current", "magnetic_field",
    "ideal_gas", "phase_transitions", "molecules", "MKT"
])
async def handle_task_callback(callback_query: types.CallbackQuery, state: FSMContext):
    task_name_prefix = callback_query.data

    max_task_numbers = {
        "dinamics": 10,
        "kinematics": 10,
        "statics": 8,
        "conservation_laws": 10,
        "oscillating_circuit": 5,
        "direct_current": 5,
        "magnetic_field": 10,
        "ideal_gas": 9,
        "phase_transitions": 7,
        "molecules": 8,
        "MKT": 10,
    }

    random_task_number = randint(1, max_task_numbers[task_name_prefix])

    task_name = f"{task_name_prefix}_{random_task_number}"
    await state.update_data(task=task_name)
    await replyTask(callback_query, task_name)

async def replyTask(callback_query: types.CallbackQuery, task_name):
    with open('tasks.json', 'r', encoding='utf-8') as file:
        tasksJSON_data = json.load(file)

    if task_name in tasksJSON_data:
        task = tasksJSON_data[task_name][0]
        await callback_query.message.edit_text(
            text=f"{task['text']}\nПример ответа: 255",
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(lambda c: c.data == "show")
async def show_solution(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    task_name = user_data.get('task')

    with open('tasks.json', 'r', encoding='utf-8') as file:
        tasksJSON_data = json.load(file)
        if task_name in tasksJSON_data:
            task = tasksJSON_data[task_name][0]
            await callback_query.message.reply_photo(
                photo=task["solution"],
                caption=f"Правильный ответ: {task['answer']}"
            )

            keyboard = InlineKeyboardBuilder().add(
                InlineKeyboardButton(text="Продолжить", callback_data=task_name.split('_')[0])
            ).adjust(1)
            await callback_query.message.answer(
                text="Хотите ли вы продолжить с следующей задачей?",
                reply_markup=keyboard.as_markup()
            )

@dp.message(lambda message: True)
async def check_answer(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    task_name = user_data.get('task')

    if "math" in task_name:
        file_name = 'math.json'
        callback_data_show = "show_math"
    else:
        file_name = 'tasks.json'
        callback_data_show = "show"

    with open(file_name, 'r', encoding='utf-8') as file:
        tasksJSON_data = json.load(file)
        if task_name in tasksJSON_data:
            task = tasksJSON_data[task_name][0]
            user_answer = message.text.replace(',', '.').strip()
            correct_answer = str(task['answer']).replace(',', '.').strip()

            if user_answer == correct_answer:
                await state.clear()
                keyboard = InlineKeyboardBuilder().add(InlineKeyboardButton(text="Меню", callback_data="start"),
                        InlineKeyboardButton(text="Продолжить", callback_data=task_name.rsplit('_', 1)[0]))
                await message.answer("Ответ правильный!", reply_markup=keyboard.as_markup())
            else:
                keyboard = InlineKeyboardBuilder().add(
                        InlineKeyboardButton(text="Показать", callback_data=callback_data_show),
                        InlineKeyboardButton(text="Продолжить", callback_data=task_name.rsplit('_', 1)[0]))
                await message.answer(
                    text="Ответ неправильный! Хотите ли вы посмотреть решение с объяснением или продолжить с новой задачей?",
                    reply_markup=keyboard.as_markup()
                )

#МАТЕМАТИКА

@dp.callback_query(lambda c: c.data in [
    "math_geometry_plosk", "math_vektor", "math_stereometry", "math_probability",
    "math_hard_probability", "math_equation", "math_expressions",
    "math_function", "math_text", "math_text_two", "math_graph", "math_derivative"
])
async def handle_task_callback(callback_query: types.CallbackQuery, state: FSMContext):
    task_name_prefix = callback_query.data

    max_task_numbers = {
        "math_geometry_plosk": 10,
        "math_vektor": 10,
        "math_stereometry": 10,
        "math_probability": 10,
        "math_hard_probability": 10,
        "math_equation": 10,
        "math_expressions": 10,
        "math_function": 10,
        "math_text": 10,
        "math_text_two": 10,
        "math_graph": 10,
        "math_derivative": 10,
    }

    random_task_number = randint(1, max_task_numbers[task_name_prefix])

    task_name = f"{task_name_prefix}_{random_task_number}"
    await state.update_data(task=task_name)
    await replyTaskMath(callback_query, task_name)

async def replyTaskMath(callback_query: types.CallbackQuery, task_name):
    with open('math.json', 'r', encoding='utf-8') as file:
        tasksJSON_data = json.load(file)
    if task_name in tasksJSON_data:
        task = tasksJSON_data[task_name][0]
        if len(task) == 4:
            await callback_query.message.answer_photo(
                photo=task['photo'],
                caption=f"{task['text']}\nПример ответа: 255",
                parse_mode=ParseMode.HTML)
        elif len(task) == 3 and "photo" in task:
            await callback_query.message.answer_photo(
                photo=task['photo'],
                caption="Пример ответа: 255",
                parse_mode=ParseMode.HTML)
        elif len(task) == 3 and "text" in task:
            await callback_query.message.answer(
                text=f"{task['text']}\nПример ответа: 255",
                parse_mode=ParseMode.HTML
            )


@dp.callback_query(lambda c: c.data == "show_math")
async def show_solution(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    task_name = user_data.get('task')

    with open('math.json', 'r', encoding='utf-8') as file:
        tasksJSON_data = json.load(file)
        if task_name in tasksJSON_data:
            task = tasksJSON_data[task_name][0]
            await callback_query.message.reply_photo(
                photo=task["solution"],
                caption=f"Правильный ответ: {task['answer']}"
            )

            keyboard = InlineKeyboardBuilder().add(
                InlineKeyboardButton(text="Продолжить", callback_data=task_name.rsplit('_', 1)[0])
            ).adjust(1)
            await callback_query.message.answer(
                text="Хотите ли вы продолжить с следующей задачей?",
                reply_markup=keyboard.as_markup()
            )

user_quiz_type = {}
QUIZ_TYPE_STRESS = "stress_quiz"
QUIZ_TYPE_INF = "inf_quiz"

@dp.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id

    quiz_type = user_quiz_type.get(user_id)

    if quiz_type == QUIZ_TYPE_STRESS:
        await send_random_quiz(user_id)
    elif quiz_type == QUIZ_TYPE_INF:
        chat_id = poll_answer.user.id
        await send_quiz_inf(user_id, chat_id)


async def send_random_quiz(user_id: int):
    quiz = stress.get_random_quiz()

    await bot.send_poll(chat_id=user_id,
                        question=f'Поставь правильное ударение в слове {quiz.question.upper()}',
                        options=quiz.options,
                        type='quiz',
                        correct_option_id=quiz.correct_number,
                        is_anonymous=False)
    user_quiz_type[user_id] = QUIZ_TYPE_STRESS

async def send_quiz_inf(chat_id: int, user_id: int):
    question_index = user_data.get(user_id, 0)

    # Проверяем, есть ли ещё вопросы
    if question_index < len(questions):
        question_data = questions[question_index]
        await bot.send_poll(
            chat_id=chat_id,
            question=question_data['question'],
            options=question_data['options'],
            type='quiz',
            correct_option_id=question_data['correct_option_id'],
            is_anonymous=False
        )
        user_quiz_type[user_id] = QUIZ_TYPE_INF
        user_data[user_id] = question_index + 1  # Обновляем индекс вопроса для пользователя
    else:
        await bot.send_message(chat_id, "Вы завершили тест!")
        user_data.pop(user_id, None)  # Удаляем данные пользователя после завершения теста


def get_hour_declension(hours: int) -> str:
    if 11 <= hours % 100 <= 14:
        return "часов"
    last_digit = hours % 10
    if last_digit == 1:
        return "час"
    elif 2 <= last_digit <= 4:
        return "часа"
    else:
        return "часов"

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())