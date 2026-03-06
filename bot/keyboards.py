from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.content import INCIDENTS, QUIZ, TOPICS


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Разделы"), KeyboardButton(text="🧭 Чек-лист")],
            [KeyboardButton(text="⚠️ Кейсы"), KeyboardButton(text="🛟 Что делать?")],
            [KeyboardButton(text="🧪 Тест"), KeyboardButton(text="📁 Источники")],
            [KeyboardButton(text="🔎 Поиск")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел или введи запрос...",
    )


def topics_kb():
    builder = InlineKeyboardBuilder()
    for slug, topic in TOPICS.items():
        builder.add(InlineKeyboardButton(text=topic["title"], callback_data=f"topic:{slug}"))
    builder.adjust(1)
    return builder.as_markup()


def incidents_kb():
    builder = InlineKeyboardBuilder()
    for key, incident in INCIDENTS.items():
        builder.add(InlineKeyboardButton(text=incident["title"], callback_data=f"incident:{key}"))
    builder.adjust(1)
    return builder.as_markup()


def quiz_kb(question_index: int):
    builder = InlineKeyboardBuilder()
    for option_index, option in enumerate(QUIZ[question_index]["options"]):
        builder.add(
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz:{question_index}:0:{option_index}",
            )
        )
    builder.adjust(1)
    return builder.as_markup()
