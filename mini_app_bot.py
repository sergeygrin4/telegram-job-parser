import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from telegram import Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from threading import Thread

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('7952407611:AAF_J8xFIE4FEL5Kmf6cFMUL0BZaEQsn_7s')
MANAGER_CHAT_ID = os.getenv('794618749')
SHARED_SECRET = os.getenv('SHARED_SECRET', 'v04Ls7_UWsqb4XHQz9tYwtH6m2A0KHw4')
PORT = int(os.getenv('PORT', 8000))
WEB_APP_URL = os.getenv('WEB_APP_URL', 'telegram-job-parser-production.up.railway.app')

app = Flask(__name__, static_folder='static')
CORS(app)

# Глобальная переменная для бота
bot_app = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start с кнопкой для открытия мини-апа"""
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🔍 Открыть поиск вакансий",
                "web_app": {"url": f"{WEB_APP_URL}/index.html"}
            }
        ]]
    }
    
    await update.message.reply_text(
        "👋 Привет! Нажми на кнопку ниже, чтобы открыть поиск вакансий:",
        reply_markup=keyboard
    )

async def send_telegram_message(chat_id: str, message: str):
    """Отправка сообщения через Telegram бота"""
    if bot_app and bot_app.bot:
        try:
            await bot_app.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "telegram-job-parser"})

@app.route('/post', methods=['POST'])
def post_job():
    """Endpoint для получения вакансий от парсера"""
    # Проверка секретного ключа
    secret = request.headers.get('X-SECRET')
    if secret != SHARED_SECRET:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.json
        chat_title = data.get('chat_title', 'Неизвестный канал')
        text = data.get('text', '')
        link = data.get('link', '')
        
        # Формирование сообщения для менеджера
        message = f"📋 <b>Новая вакансия</b>\n\n"
        message += f"📢 Канал: {chat_title}\n"
        message += f"📝 Текст: {text}\n"
        if link:
            message += f"🔗 Ссылка: {link}\n"
        
        # Отправка сообщения
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            send_telegram_message(MANAGER_CHAT_ID, message)
        )
        loop.close()
        
        if result:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"error": "Failed to send message"}), 500
            
    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def root():
    """Главная страница"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Статические файлы"""
    return send_from_directory('static', path)

def run_flask():
    """Запуск Flask сервера"""
    app.run(host='0.0.0.0', port=PORT, debug=False)

async def run_bot():
    """Запуск Telegram бота"""
    global bot_app
    
    bot_app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    bot_app.add_handler(CommandHandler("start", start_command))
    
    # Запуск бота
    await bot_app.initialize()
    await bot_app.start()
    logger.info("Бот запущен")
    
    # Держим бота активным
    await bot_app.updater.start_polling()
    await asyncio.Event().wait()

def main():
    """Главная функция запуска"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен!")
        return
    
    if not MANAGER_CHAT_ID:
        logger.error("MANAGER_CHAT_ID не установлен!")
        return
    
    logger.info(f"Запуск сервера на порту {PORT}")
    logger.info(f"Web App URL: {WEB_APP_URL}")
    
    # Запуск Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запуск бота
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Остановка сервера...")

if __name__ == '__main__':
    main()
