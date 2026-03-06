import asyncio
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

from bot.content import (
    GLOSSARY_TEXT,
    HELP_TEXT,
    INCIDENTS,
    LIABILITY_TEXT,
    MYTHS,
    QUIZ,
    ROLE_GUIDES,
    SEARCH_HINT,
    START_TEXT,
    TEMPLATE_TEXTS,
    THEORY_TOPICS,
    format_incident,
    format_myth,
    format_quiz_question,
    format_quiz_result,
    format_role_guide,
    format_sources,
    format_template,
    format_theory_topic,
)
from bot.keyboards import (
    incidents_kb,
    main_menu_kb,
    myths_kb,
    quiz_kb,
    roles_kb,
    templates_kb,
    theory_kb,
)
from bot.utils import search_materials, split_text

load_dotenv()

router = Router()


class SearchState(StatesGroup):
    waiting_query = State()


async def send_long_message(message: Message, text: str):
    for chunk in split_text(text):
        await message.answer(chunk, reply_markup=main_menu_kb())


async def send_long_callback(callback: CallbackQuery, text: str):
    for chunk in split_text(text):
        await callback.message.answer(chunk, reply_markup=main_menu_kb())


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TEXT, reply_markup=main_menu_kb())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu_kb())


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) == 2 and parts[1].strip():
        await send_long_message(message, search_materials(parts[1].strip()))
        return
    await state.set_state(SearchState.waiting_query)
    await message.answer(SEARCH_HINT, reply_markup=main_menu_kb())


@router.message(F.text == "📚 Теория")
async def open_theory(message: Message):
    await message.answer("Выбери большой теоретический раздел:", reply_markup=theory_kb())


@router.message(F.text == "🧠 Глоссарий")
async def open_glossary(message: Message):
    await send_long_message(message, GLOSSARY_TEXT)


@router.message(F.text == "⚖️ Ответственность")
async def open_liability(message: Message):
    await send_long_message(message, LIABILITY_TEXT)


@router.message(F.text == "🎯 По ролям")
async def open_roles(message: Message):
    await message.answer("Выбери роль — бот покажет приоритеты и риски:", reply_markup=roles_kb())


@router.message(F.text == "🧭 Чек-лист")
async def open_checklist(message: Message):
    await send_long_message(message, format_theory_topic("checklist"))


@router.message(F.text == "⚠️ Кейсы")
async def open_cases(message: Message):
    await send_long_message(message, format_theory_topic("cases"))
    await message.answer("Нужен быстрый алгоритм? Выбери инцидент:", reply_markup=incidents_kb())


@router.message(F.text == "🛟 Инциденты")
async def open_incidents(message: Message):
    await message.answer("Выбери рабочую ситуацию — бот покажет порядок действий:", reply_markup=incidents_kb())


@router.message(F.text == "🧾 Шаблоны")
async def open_templates(message: Message):
    await message.answer("Выбери шаблон или памятку:", reply_markup=templates_kb())


@router.message(F.text == "💡 Мифы")
async def open_myths(message: Message):
    await message.answer("Выбери миф — бот покажет, где ошибка в рассуждении:", reply_markup=myths_kb())


@router.message(F.text == "📁 Источники")
async def open_sources(message: Message):
    await send_long_message(message, format_sources())


@router.message(F.text == "🔎 Поиск")
async def open_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await message.answer(SEARCH_HINT, reply_markup=main_menu_kb())


@router.message(F.text == "🧪 Тест")
async def start_quiz(message: Message):
    await message.answer(format_quiz_question(0), reply_markup=quiz_kb(0, 0))


@router.callback_query(F.data.startswith("topic:"))
async def topic_callback(callback: CallbackQuery):
    slug = callback.data.split(":", 1)[1]
    if slug not in THEORY_TOPICS:
        await callback.answer("Раздел не найден", show_alert=True)
        return
    await callback.answer()
    await send_long_callback(callback, format_theory_topic(slug))


@router.callback_query(F.data.startswith("incident:"))
async def incident_callback(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in INCIDENTS:
        await callback.answer("Сценарий не найден", show_alert=True)
        return
    await callback.answer()
    await send_long_callback(callback, format_incident(key))


@router.callback_query(F.data.startswith("role:"))
async def role_callback(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in ROLE_GUIDES:
        await callback.answer("Роль не найдена", show_alert=True)
        return
    await callback.answer()
    await send_long_callback(callback, format_role_guide(key))


@router.callback_query(F.data.startswith("myth:"))
async def myth_callback(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in MYTHS:
        await callback.answer("Миф не найден", show_alert=True)
        return
    await callback.answer()
    await send_long_callback(callback, format_myth(key))


@router.callback_query(F.data.startswith("template:"))
async def template_callback(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    if key not in TEMPLATE_TEXTS:
        await callback.answer("Шаблон не найден", show_alert=True)
        return
    await callback.answer()
    await send_long_callback(callback, format_template(key))


@router.callback_query(F.data.startswith("quiz:"))
async def quiz_callback(callback: CallbackQuery):
    _, q_index, score, selected = callback.data.split(":")
    q_index = int(q_index)
    score = int(score)
    selected = int(selected)

    if QUIZ[q_index]["correct"] == selected:
        score += 1

    next_index = q_index + 1
    await callback.answer("Ответ принят")

    if next_index < len(QUIZ):
        await callback.message.edit_text(
            format_quiz_question(next_index),
            reply_markup=quiz_kb(next_index, score),
        )
        return

    await callback.message.edit_text(format_quiz_result(score, len(QUIZ)))
    await callback.message.answer("Тест завершён. Открой теорию, роли или мифы для повторения.", reply_markup=main_menu_kb())


@router.message(SearchState.waiting_query)
async def process_search(message: Message, state: FSMContext):
    query = (message.text or "").strip()
    await state.clear()
    if not query:
        await message.answer("Запрос пустой. Напиши ключевое слово или фразу.", reply_markup=main_menu_kb())
        return
    await send_long_message(message, search_materials(query))


@router.message()
async def fallback(message: Message):
    text = (message.text or "").strip()
    if not text:
        return
    await send_long_message(message, search_materials(text))


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN. Создай .env на основе .env.example")

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
