import asyncio
import logging
from datetime import datetime, timedelta
import sqlite3
from typing import Dict
import os
from pathlib import Path
import json
from functools import lru_cache
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramAPIError

# FSM / FSM
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Логирование / Logging
logging.basicConfig(level=logging.INFO)  # Настройка логирования / Setup logging
logger = logging.getLogger(__name__)

# Загрузка .env / Load .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("BOT_TOKEN отсутствует!")  # BOT_TOKEN not found

DATABASE_NAME = os.getenv("DATABASE_NAME", "reminders.db")

# Локализация / Localization
LOCALES_DIR = Path(__file__).parent / "locales"
LANGUAGES = {
    "ru": LOCALES_DIR / "ru.json",
    "en": LOCALES_DIR / "en.json",
}

@lru_cache(maxsize=None)
def load_translations_cached(lang: str) -> Dict[str, str]:  # Загружает переводы / Load translations
    file = LANGUAGES.get(lang)
    if file and file.exists():
        return json.load(open(file, encoding="utf-8"))
    # fallback русский / fallback Russian
    return json.load(open(LANGUAGES["ru"], encoding="utf-8"))

def get_text(lang: str, key: str, **kwargs):
    text = load_translations_cached(lang).get(key, f"MISSING:{key}")
    try:
        return text.format(**kwargs)
    except KeyError:
        return text

# FSM состояния / FSM states
class ReminderFSM(StatesGroup):
    waiting_text = State()  # Ждём текст напоминания / Waiting for reminder text
    waiting_time = State()  # Ждём время напоминания / Waiting for reminder time

# Работа с базой данных / Database operations
class ReminderDatabase:
    def __init__(self, name):
        self.name = name
        self.init_db()

    def init_db(self):  # Инициализация таблиц / Init DB tables
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru'
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reminder_text TEXT,
                reminder_time TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_user_language(self, uid: int) -> str:  # Получение языка пользователя / Get user language
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("SELECT language FROM users WHERE user_id=?", (uid,))
        res = cur.fetchone()
        conn.close()
        if res:
            return res[0]
        self.set_user_language(uid, "ru")
        return "ru"

    def set_user_language(self, uid: int, lang: str):  # Установка языка пользователя / Set user language
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?,?)", (uid, lang))
        conn.commit()
        conn.close()

    def add_reminder(self, uid: int, text: str, time: str):  # Добавление напоминания / Add reminder
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("INSERT INTO reminders (user_id, reminder_text, reminder_time) VALUES (?,?,?)",
                    (uid, text, time))
        conn.commit()
        conn.close()

    def get_user_reminders(self, uid: int):  # Получение всех напоминаний пользователя / Get user reminders
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("SELECT id, reminder_text, reminder_time FROM reminders WHERE user_id=? ORDER BY reminder_time",
                    (uid,))
        data = cur.fetchall()
        conn.close()
        return data

    def get_due_reminders(self, now_str: str):  # Получение "сработавших" напоминаний / Get due reminders
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, reminder_text FROM reminders WHERE reminder_time<=?", (now_str,))
        data = cur.fetchall()
        conn.close()
        return data

    def remove(self, rid: int):  # Удаление напоминания / Remove reminder
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute("DELETE FROM reminders WHERE id=?", (rid,))
        conn.commit()
        conn.close()

db = ReminderDatabase(DATABASE_NAME)

# Инициализация бота / Bot init
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Команды / Commands
@dp.message(Command("start"))
async def cmd_start(message: Message):
    lang = db.get_user_language(message.from_user.id)  # Получаем язык / Get language
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "button_change_language"), callback_data="change_lang")]
        ]
    )
    await message.answer(get_text(lang, "welcome", first_name=message.from_user.first_name), reply_markup=kb)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    lang = db.get_user_language(message.from_user.id)
    await message.answer(get_text(lang, "help_text"))

# Установка напоминания / Set reminder
@dp.message(Command("set_reminder"))
async def set_reminder_start(message: Message, state: FSMContext):
    lang = db.get_user_language(message.from_user.id)
    await state.set_state(ReminderFSM.waiting_text)
    await message.answer(get_text(lang, "prompt_text"))

@dp.message(ReminderFSM.waiting_text)
async def reminder_text(message: Message, state: FSMContext):
    if not message.text.strip():
        lang = db.get_user_language(message.from_user.id)
        await message.answer(get_text(lang, "empty_text_error"))
        return
    await state.update_data(text=message.text.strip())
    lang = db.get_user_language(message.from_user.id)
    await state.set_state(ReminderFSM.waiting_time)
    await message.answer(get_text(lang, "prompt_time"))

@dp.message(ReminderFSM.waiting_time)
async def reminder_time(message: Message, state: FSMContext):
    lang = db.get_user_language(message.from_user.id)
    try:
        h, m = map(int, message.text.split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
    except:
        await message.answer(get_text(lang, "invalid_time_format"))
        return

    now = datetime.now()
    rem = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if rem <= now:
        rem += timedelta(days=1)

    data = await state.get_data()
    db.add_reminder(message.from_user.id, data["text"], rem.strftime("%Y-%m-%d %H:%M:%S"))
    await state.clear()
    await message.answer(get_text(lang, "reminder_set_success",
                                  text=data["text"],
                                  time=rem.strftime("%d.%m.%Y %H:%M")))

# Список напоминаний / List reminders
@dp.message(Command("list_reminders"))
async def list_reminders(message: Message):
    lang = db.get_user_language(message.from_user.id)
    rems = db.get_user_reminders(message.from_user.id)
    if not rems:
        await message.answer(get_text(lang, "no_reminders"))
        return
    txt = get_text(lang, "active_reminders_header")
    for rid, t, time_str in rems:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        txt += get_text(lang, "reminder_item",
                        id=rid,
                        text=t,
                        time=dt.strftime("%d.%m.%Y %H:%M"))
    await message.answer(txt)

# Смена языка / Change language
@dp.message(Command("change_language"))
async def cmd_change_language(message: Message):
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Русский(Russian)", callback_data="lang_ru")],
            [InlineKeyboardButton(text="English(Английский)", callback_data="lang_en")]
        ]
    )
    
    await message.answer(get_text(lang, "choose_language"), reply_markup=kb)
@dp.callback_query(F.data == "change_lang")
async def change_lang(callback: CallbackQuery):
    lang = db.get_user_language(callback.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский(Russian)", callback_data="lang_ru")],
        [InlineKeyboardButton(text="English(Английский)", callback_data="lang_en")]
    ])
    await callback.message.edit_text(get_text(lang, "choose_language"), reply_markup=kb)
    await callback.answer()

@dp.callback_query(F.data.startswith("lang_"))
async def lang_select(callback: CallbackQuery):
    new_lang = callback.data.split("_")[1]
    db.set_user_language(callback.from_user.id, new_lang)
    lang = db.get_user_language(callback.from_user.id)
    key = "lang_changed_to_ru" if new_lang == "ru" else "lang_changed_to_en"
    await callback.message.edit_text(get_text(lang, key))
    await callback.answer()


# Кнопки Done / Not Done
@dp.callback_query(F.data.startswith("done_"))
async def done(callback: CallbackQuery):
    lang = db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(callback.message.html_text + "\n\n" + get_text(lang, "reminder_done"))
    await callback.answer(get_text(lang, "reminder_done_response"))

@dp.callback_query(F.data.startswith("not_done_"))
async def not_done(callback: CallbackQuery):
    lang = db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(callback.message.html_text + "\n\n" + get_text(lang, "reminder_not_done"))
    await callback.answer(get_text(lang, "reminder_not_done_response"))

# Фоновая задача для отправки напоминаний / Background task for reminders
async def send_scheduled_reminders():
    while True:
        await asyncio.sleep(30)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        due = db.get_due_reminders(now)
        if not due:
            continue
        for rid, uid, text in due:
            lang = db.get_user_language(uid)
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(lang, "button_done"), callback_data=f"done_{rid}")],
                [InlineKeyboardButton(text=get_text(lang, "button_not_done"), callback_data=f"not_done_{rid}")]
            ])
            try:
                await bot.send_message(uid, f"⏰ {get_text(lang,'reminder_label')}: <b>{text}</b>", reply_markup=kb)
                db.remove(rid)
            except TelegramAPIError as e:
                logger.error(f"Ошибка при отправке / Error sending reminder {rid} to {uid}: {e}")

# -------------------------------------------------------------------
# Main
async def main():
    scheduler = asyncio.create_task(send_scheduled_reminders())
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        scheduler.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
