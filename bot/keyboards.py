from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.content import INCIDENTS, MYTHS, QUIZ, ROLE_GUIDES, TEMPLATE_TEXTS, THEORY_TOPICS


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Теория"), KeyboardButton(text="🧠 Глоссарий")],
            [KeyboardButton(text="⚖️ Ответственность"), KeyboardButton(text="🎯 По ролям")],
            [KeyboardButton(text="🧭 Чек-лист"), KeyboardButton(text="⚠️ Кейсы")],
            [KeyboardButton(text="🛟 Инциденты"), KeyboardButton(text="🧾 Шаблоны")],
            [KeyboardButton(text="💡 Мифы"), KeyboardButton(text="🧪 Тест")],
            [KeyboardButton(text="📁 Источники"), KeyboardButton(text="🔎 Поиск")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел или введи запрос...",
    )



def theory_kb():
    builder = InlineKeyboardBuilder()
    for slug, topic in THEORY_TOPICS.items():
        if slug in {"checklist", "cases"}:
            continue
        builder.add(InlineKeyboardButton(text=topic["title"], callback_data=f"topic:{slug}"))
    builder.adjust(1)
    return builder.as_markup()



def incidents_kb():
    builder = InlineKeyboardBuilder()
    for key, incident in INCIDENTS.items():
        builder.add(InlineKeyboardButton(text=incident["title"], callback_data=f"incident:{key}"))
    builder.adjust(1)
    return builder.as_markup()



def roles_kb():
    builder = InlineKeyboardBuilder()
    for key, guide in ROLE_GUIDES.items():
        builder.add(InlineKeyboardButton(text=guide["title"], callback_data=f"role:{key}"))
    builder.adjust(1)
    return builder.as_markup()



def myths_kb():
    builder = InlineKeyboardBuilder()
    for key, myth in MYTHS.items():
        builder.add(InlineKeyboardButton(text=myth["title"], callback_data=f"myth:{key}"))
    builder.adjust(1)
    return builder.as_markup()



def templates_kb():
    builder = InlineKeyboardBuilder()
    for key, item in TEMPLATE_TEXTS.items():
        builder.add(InlineKeyboardButton(text=item["title"], callback_data=f"template:{key}"))
    builder.adjust(1)
    return builder.as_markup()



def quiz_kb(question_index: int, score: int):
    builder = InlineKeyboardBuilder()
    for option_index, option in enumerate(QUIZ[question_index]["options"]):
        builder.add(
            InlineKeyboardButton(
                text=option,
                callback_data=f"quiz:{question_index}:{score}:{option_index}",
            )
        )
    builder.adjust(1)
    return builder.as_markup()
