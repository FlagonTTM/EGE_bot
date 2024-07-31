from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
start = InlineKeyboardBuilder().add(InlineKeyboardButton(text="Информатика", callback_data='subject_informatics'),
             InlineKeyboardButton(text="Физика", callback_data='subject_physics'),
             InlineKeyboardButton(text="Русский", callback_data='subject_russian'),
             InlineKeyboardButton(text="Проф математика", callback_data='subject_math'),
             InlineKeyboardButton(text="Напоминание", callback_data='subject_napom')).adjust(2)
start_phys = InlineKeyboardBuilder().add(InlineKeyboardButton(text="Механика", callback_data='phys_mechanics'),
             InlineKeyboardButton(text="Электродинамика", callback_data='phys_electrodynamics'),
             InlineKeyboardButton(text="Термодинамика", callback_data='phys_thermodynamics'),
             InlineKeyboardButton(text="Молекулярная физика", callback_data='phys_Molecular Physics')).adjust(2)
start_math = InlineKeyboardBuilder().add(InlineKeyboardButton(text="1 Планиметрия", callback_data='math_geometry_plosk'),
             InlineKeyboardButton(text="2 Векторы", callback_data='math_vektor'),
             InlineKeyboardButton(text="3 Стереометрия", callback_data='math_stereometry'),
             InlineKeyboardButton(text="4 Простая теория вероятности", callback_data='math_probability'),
            InlineKeyboardButton(text="5 Сложная теория вероятности", callback_data='math_hard_probability'),
            InlineKeyboardButton(text="6 Уравнения", callback_data='math_equation'),
            InlineKeyboardButton(text="7 Числ. и букв. выражения", callback_data='math_expressions'),
            InlineKeyboardButton(text="8 График функции", callback_data='math_function'),
            InlineKeyboardButton(text="9 Расчёты", callback_data='math_text'),
            InlineKeyboardButton(text="10 Текстовая задача", callback_data='math_text_two'),
            InlineKeyboardButton(text="11 График функции", callback_data='math_graph'),
            InlineKeyboardButton(text="12 Исследование функции", callback_data='math_derivative')).adjust(1)
kb = [
    [
        types.KeyboardButton(text="Меню"),
        types.KeyboardButton(text="Отменить напоминание")
    ],
]
menu = types.ReplyKeyboardMarkup(
    keyboard=kb,one_time_keyboard=False,resize_keyboard=True)