# ⏰ Reminder Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Многофункциональный Telegram бот для создания и управления напоминаниями с поддержкой русского и английского языков.**

**A feature-rich Telegram bot for creating and managing reminders with Russian and English language support.**

---

## ✨ Возможности / Features

-   **📝 Создание напоминаний:** Легко устанавливайте напоминания, указывая текст и время в формате `ЧЧ:ММ`.
    -   *Set Reminders: Easily set reminders by specifying text and time in `HH:MM` format.*
-   **⏰ Мгновенные уведомления:** Бот автоматически проверяет и отправляет напоминания точно в указанное время.
    -   *Instant Notifications: The bot automatically checks and sends reminders exactly at the specified time.*
-   **✅ Интерактивные кнопки:** Отмечайте напоминания как "Выполнено" или "Не выполнено" с помощью удобных inline-кнопок.
    -   *Interactive Buttons: Mark reminders as "Done" or "Not Done" using convenient inline buttons.*
-   **📋 Просмотр списка:** Получайте список всех ваших активных напоминаний одной командой.
    -   *List View: Get a list of all your active reminders with a single command.*
-   **🌐 Поддержка двух языков:** Полная локализация на русский и английский с возможностью быстрого переключения.
    -   *Bilingual Support: Full localization in Russian and English with a quick switch option.*
-   **🔒 Надежность:** Использование базы данных `SQLite` для хранения данных и `FSM` для управления состояниями обеспечивает стабильную работу.
    -   *Reliability: Uses an `SQLite` database for data storage and `FSM` for state management, ensuring stable operation.*

---

## ⚙️ Установка / Installation

1.  **Клонируйте репозиторий или создайте проект:**
    -   *Clone the repository or create a project folder:*
    ```bash
    mkdir reminder_bot && cd reminder_bot
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    -   *Create and activate a virtual environment:*
    ```bash
    # Для Windows / For Windows
    python -m venv venv
    venv\Scripts\activate

    # Для macOS/Linux / For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Установите зависимости:**
    -   *Install dependencies:*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройте файл `.env`:**
    -   *Configure the `.env` file:*
    Создайте файл `.env` в корневой папке и добавьте в него токен вашего бота.
    -   *Create a `.env` file in the root folder and add your bot token to it.*
    ```env
    BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
    DATABASE_NAME=reminders.db
    ```

---

## 🚀 Запуск / Run

1.  **Активируйте виртуальное окружение (если не активно).**
    -   *Activate the virtual environment (if not already active).*

2.  **Запустите бота:**
    -   *Run the bot:*
    ```bash
    python bot.py
    ```
    > **⚠️ Важно / Important:**
    > Запускайте только один экземпляр бота, чтобы избежать ошибки `Conflict: terminated by other getUpdates request`.
    > *Run only one bot instance at a time to avoid the `Conflict: terminated by other getUpdates request` error.*

---

## 📝 Команды / Usage

-   `/start` — Начать работу с ботом, получить приветствие и кнопку смены языка.
    -   *Start the bot, receive a greeting, and a language change button.*
-   `/help` — Показать список доступных команд.
    -   *Show the list of available commands.*
-   `/set_reminder` — Создать новое напоминание.
    -   *Create a new reminder.*
-   `/list_reminders` — Показать все активные напоминания.
    -   *Show all active reminders.*
-   `/change_language` — Открыть меню для смены языка.
    -   *Open the language selection menu.*

---

## 📂 Структура проекта / Project Structure

```
reminder_bot/
│
├── .env                # Файл с переменными окружения (токен) / Environment variables (token)
├── bot.py              # Основной файл логики бота / Main bot logic file
├── requirements.txt    # Список зависимостей / List of dependencies
├── reminders.db        # База данных SQLite для хранения напоминаний / SQLite database
└── locales/            # Папка с файлами локализации / Localization files
    ├── en.json
    └── ru.json
```

---

## 🌍 Локализация / Localization

Все тексты, которые бот отправляет пользователю, хранятся в файлах `ru.json` и `en.json` в папке `locales/`. Это позволяет легко добавлять новые языки или изменять существующие фразы.

*All texts sent by the bot are stored in `ru.json` and `en.json` files within the `locales/` folder. This makes it easy to add new languages or modify existing phrases.*

**Пример / Example (`en.json`):**
```json
{
  "welcome": "Hello, {first_name}!",
  "help_text": "Available commands: /start, /help, /set_reminder, /list_reminders, /change_language",
  "prompt_text": "Enter the reminder text:",
  "reminder_set_success": "Reminder '{text}' has been set for {time}.",
  "button_done": "✅ Done",
  "button_not_done": "❌ Not Done"
}
```

---

## 👨‍💻 Автор / Author

-   **Салих / Salikh** — Python-разработчик.
    -   *Python developer.*
-   **Контакты / Contacts:**
    -   [Freelance.ru](https://freelance.ru/example)
    -   [Instagram](https://instagram.com/example)
    -   [Telegram-канал - Channel](https://t.me/example_channel)
    -   [Telegram ЛС - Contacts ](https://t.me/example_user)
    -   [GitHub] ((https://github.com/salihhhh014/))

---

## 💖 Поддержка / Support

Если вам понравился проект, вы можете поддержать автора:
*If you like this project, you can support the author:*

-   [**DonationAlerts**](https://www.donationalerts.com/r/salihhhh_1120)


## Примечание / Note
    Данный бот эксперминтальный поэтому могут быть ошибки.И также он будет со временем обновляться следите!
    This bot is experimental, so there may be some bugs. It will also be updated over time, stay tuned!