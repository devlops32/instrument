from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from parser import parse_chat, invite_users
from utils import count_users
from keyboards import main_reply_kb, after_parse_kb

router = Router()

class ParserStates(StatesGroup):
    waiting_for_parse_link = State()
    waiting_for_invite_link = State()

@router.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        "👋 Привет! Я бот для парсинга и инвайта участников.\n\n"
        "Используй кнопки ниже или команды:\n"
        "/parse - парсить участников (автовступление)\n"
        "/invite - пригласить всех (автовступление)\n"
        "/stats - статистика\n"
        "/help - помощь",
        reply_markup=main_reply_kb()
    )

@router.message(Command("help"))
async def help_cmd(msg: types.Message):
    await msg.answer(
        "📖 Инструкция:\n"
        "1. Нажми 'Парсить' и отправь ссылку на канал/чат\n"
        "2. Бот автоматически вступит в цель (если нужно)\n"
        "3. Участники сохранятся в users.txt\n"
        "4. Нажми 'Инвайтить' и отправь ссылку куда приглашать\n"
        "5. Бот автоматически вступит и пригласит всех\n\n"
        "Формат: @username или https://t.me/...\n"
        "⚠️ Для инвайта нужны права администратора в цели",
        reply_markup=main_reply_kb()
    )

@router.message(Command("stats"))
async def stats_cmd(msg: types.Message):
    count = count_users()
    await msg.answer(f"📊 В базе {count} участников", reply_markup=main_reply_kb())

@router.message(Command("parse"))
async def parse_cmd(msg: types.Message, state: FSMContext):
    await msg.answer(
        "📥 Отправь ссылку на канал/чат\n"
        "Бот автоматически вступит, если его там нет\n"
        "Пример: @username или https://t.me/...",
        reply_markup=main_reply_kb()
    )
    await state.set_state(ParserStates.waiting_for_parse_link)

@router.message(Command("invite"))
async def invite_cmd(msg: types.Message, state: FSMContext):
    count = count_users()
    if count == 0:
        return await msg.answer("❌ Сначала наполни базу через /parse", reply_markup=main_reply_kb())
    await msg.answer(
        f"📤 В базе {count} человек. Отправь ссылку куда приглашать\n"
        "Бот автоматически вступит, если нужно",
        reply_markup=main_reply_kb()
    )
    await state.set_state(ParserStates.waiting_for_invite_link)

@router.message(F.text == "📥 Парсить")
async def parse_btn(msg: types.Message, state: FSMContext):
    await parse_cmd(msg, state)

@router.message(F.text == "📤 Инвайтить")
async def invite_btn(msg: types.Message, state: FSMContext):
    await invite_cmd(msg, state)

@router.message(F.text == "📊 Статистика")
async def stats_btn(msg: types.Message):
    await stats_cmd(msg)

@router.message(F.text == "ℹ️ Помощь")
async def help_btn(msg: types.Message):
    await help_cmd(msg)

@router.message(ParserStates.waiting_for_parse_link)
async def process_parse_link(msg: types.Message, state: FSMContext):
    link = msg.text.strip()
    if not link:
        return await msg.answer("❌ Пустая ссылка")
    
    await msg.answer("⏳ Вступаю и парсю...")
    try:
        count = await parse_chat(link)
        await msg.answer(
            f"✅ Собрано {count} участников\n"
            f"Хочешь сразу пригласить их?",
            reply_markup=after_parse_kb()
        )
        await state.update_data(last_parse_link=link)
    except Exception as e:
        await msg.answer(f"❌ Ошибка: {e}", reply_markup=main_reply_kb())
    await state.clear()

@router.message(ParserStates.waiting_for_invite_link)
async def process_invite_link(msg: types.Message, state: FSMContext):
    link = msg.text.strip()
    if not link:
        return await msg.answer("❌ Пустая ссылка")
    
    await msg.answer("⏳ Вступаю и приглашаю...")
    try:
        count = await invite_users(link)
        await msg.answer(f"✅ Приглашено {count} человек", reply_markup=main_reply_kb())
    except Exception as e:
        await msg.answer(f"❌ Ошибка: {e}", reply_markup=main_reply_kb())
    await state.clear()

@router.callback_query(F.data == "parse")
async def inline_parse(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await parse_cmd(call.message, state)
    await call.answer()

@router.callback_query(F.data == "invite")
async def inline_invite(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await invite_cmd(call.message, state)
    await call.answer()

@router.callback_query(F.data == "stats")
async def inline_stats(call: types.CallbackQuery):
    await call.message.delete()
    await stats_cmd(call.message)
    await call.answer()

@router.callback_query(F.data == "help")
async def inline_help(call: types.CallbackQuery):
    await call.message.delete()
    await help_cmd(call.message)
    await call.answer()

@router.callback_query(F.data == "invite_all")
async def inline_invite_all(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    link = data.get("last_parse_link")
    if not link:
        return await call.message.answer("❌ Нет ссылки для инвайта")
    await invite_cmd(call.message, state)
    await call.answer()

@router.callback_query(F.data == "cancel")
async def inline_cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()
    await call.message.answer("❌ Отменено", reply_markup=main_reply_kb())
    await call.answer()