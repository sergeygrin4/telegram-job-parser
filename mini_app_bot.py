# mini_app_bot.py
import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

load_dotenv()

# Настройка логов
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_ID = int(os.getenv("MANAGER_ID", "0"))
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("HTTP_PORT", "8000"))
# простая проверка
if not BOT_TOKEN or not MANAGER_ID:
    log.error("Не заданы BOT_TOKEN или MANAGER_ID в окружении. Прервано.")
    raise SystemExit(1)

bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")

async def send_to_manager(chat_title: str, text: str, link: str | None = None):
    """Отправляет сообщение менеджеру с инлайн-кнопкой (если link задан)."""
    header = f"📢 *{chat_title}*\n\n"
    body = text.strip()
    kb = None
    if link:
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text="🔎 Проверить", url=link))
    try:
        await bot.send_message(chat_id=MANAGER_ID, text=header + body, reply_markup=kb)
    except Exception as e:
        log.exception("Не удалось отправить сообщение менеджеру: %s", e)

async def handle_post(request):
    """
    Ожидает JSON:
    {
      "chat_title": "...",
      "text": "...",
      "link": "https://..."   # опционно
    }
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "invalid json"}, status=400)

    chat_title = data.get("chat_title", "Без названия")
    text = data.get("text", "")
    link = data.get("link")
    # логируем
    log.info("Получен пост от парсера: %s / %s", chat_title, (text[:80] + "...") if len(text) > 80 else text)
    # Отправляем в телеграм менеджеру (делаем это асинхронно, но не блокируем ответ)
    asyncio.create_task(send_to_manager(chat_title, text, link))
    return web.json_response({"ok": True})

async def on_startup(app):
    log.info("Мини-апп запущен. Бот работает.")

async def on_cleanup(app):
    await bot.session.close()
    log.info("Shutting down bot session")

def create_app():
    app = web.Application()
    app.router.add_post("/post", handle_post)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host=HTTP_HOST, port=HTTP_PORT)

