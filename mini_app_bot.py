import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_ID = int(os.getenv("MANAGER_ID", "0"))
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("PORT", os.getenv("HTTP_PORT", "8000")))
SHARED_SECRET = os.getenv("SHARED_SECRET")  # опционально

if not BOT_TOKEN or not MANAGER_ID:
    log.error("Не заданы BOT_TOKEN или MANAGER_ID.")
    raise SystemExit(1)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

async def send_to_manager(chat_title: str, text: str, link: str | None = None):
    header = f"📢 *{chat_title}*\n\n"
    kb = None
    if link:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔎 Проверить", url=link)]]
        )
    try:
        await bot.send_message(chat_id=MANAGER_ID, text=header + text.strip(), reply_markup=kb)
    except Exception as e:
        log.exception("Не удалось отправить сообщение менеджеру: %s", e)

async def handle_post(request: web.Request):
    # простая защита по shared secret
    if SHARED_SECRET and request.headers.get("X-SECRET") != SHARED_SECRET:
        return web.json_response({"ok": False, "error": "unauthorized"}, status=401)
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "invalid json"}, status=400)

    chat_title = data.get("chat_title", "Без названия")
    text = data.get("text") or ""
    link = data.get("link")
    log.info("POST от парсера: %s / %s", chat_title, (text[:120] + "…") if len(text) > 120 else text)
    asyncio.create_task(send_to_manager(chat_title, text, link))
    return web.json_response({"ok": True})

async def on_startup(_):
    log.info("Мини-апп запущен: слушаю %s:%s", HTTP_HOST, HTTP_PORT)

async def on_cleanup(_):
    await bot.session.close()
    log.info("Bot session closed")

def create_app():
    app = web.Application()
    app.router.add_post("/post", handle_post)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host=HTTP_HOST, port=HTTP_PORT)

