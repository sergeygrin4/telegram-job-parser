import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

# Инициализация бота и диспетчера
bot = Bot(token='7952407611:AAF_J8xFIE4FEL5Kmf6cFMUL0BZaEQsn_7s')
dp = Dispatcher(bot)

# Обработчик для главной страницы (GET /)
async def handle_root(request):
    return web.Response(text="Добро пожаловать в Telegram Job Parser! Для начала выберите опцию.")

# Обработчик для POST /post (ваш текущий обработчик)
async def handle_post(request):
    data = await request.json()
    chat_title = data.get("chat_title", "")
    text = data.get("text", "")
    # Ваш код для обработки POST-запроса
    # Отправка сообщения в Telegram (например, по MANAGER_ID)
    await bot.send_message(chat_id=MANAGER_ID, text=f"Вакансия: {chat_title}\n{text}")
    return web.json_response({"status": "success"})

# Обработчик для кнопки "Начать"
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Создаем кнопки
    start_button = InlineKeyboardButton(text="Начать поиск", callback_data="start_search")
    add_group_button = InlineKeyboardButton(text="Добавить сообщество", callback_data="add_group")

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(row_width=2).add(start_button, add_group_button)

    # Отправляем сообщение с кнопками
    await bot.send_message(message.chat.id, "Добро пожаловать! Выберите опцию:", reply_markup=keyboard)

# Обработчик для добавления ссылок (POST /add_link)
async def add_link(request):
    data = await request.json()
    link = data.get("link")
    
    if link:
        # Добавление ссылки в базу данных или список
        return web.json_response({"status": "success", "message": f"Ссылка {link} добавлена"})
    else:
        return web.json_response({"status": "error", "message": "Нет ссылки"}, status=400)

# Создание приложения и роутеров
app = web.Application()

# Роуты
app.router.add_get('/', handle_root)  # Главная страница (GET /)
app.router.add_post('/post', handle_post)  # Обработчик для /post
app.router.add_post('/add_link', add_link)  # Обработчик для /add_link

# Запуск приложения на порту 8080 (или на порту, переданном через переменную окружения PORT)
port = int(os.getenv("PORT", 8080))
web.run_app(app, host="0.0.0.0", port=port)

