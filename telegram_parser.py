import asyncio
import logging
import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
MANAGER_ID = int(os.getenv("MANAGER_ID"))
SESSION_NAME = os.getenv("SESSION_NAME", "job_parser")

# Ключевые слова
KEYWORDS = [
    'вакансия','ищем','требуется','нужен','фриланс',
    'we are hiring','job offer','open position'
]

# Список чатов (username или id)
MONITORED_CHATS = [
    # 'examplegroup',        # имя группы без @
    # -1001234567890,        # id приватного чата
]

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tg-parser")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def has_keywords(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return any(k in text_lower for k in KEYWORDS)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        chat = await event.get_chat()
        chat_id = event.chat_id
        chat_title = getattr(chat, "title", "") or getattr(chat, "username", "")
        message_text = event.message.message or ""

        # Проверяем список чатов, если он указан
        if MONITORED_CHATS and str(chat_id) not in map(str, MONITORED_CHATS) and \
           getattr(chat, "username", "") not in MONITORED_CHATS:
            return

        if not has_keywords(message_text):
            return

        chat_id_stripped = str(chat_id).replace("-100", "")
        message_link = f"https://t.me/c/{chat_id_stripped}/{event.message.id}"

        text = (
            f"🔔 Найдено сообщение в чате *{chat_title or 'без названия'}*\n\n"
            f"{message_text}\n\n"
            f"{message_link}"
        )

        await client.send_message(MANAGER_ID, text, link_preview=False, parse_mode='markdown')
        log.info("✅ Сообщение отправлено менеджеру из чата: %s", chat_title)
    except Exception as e:
        log.exception("Ошибка при обработке сообщения: %s", e)

import os, requests, logging
log = logging.getLogger(__name__)

BOT_API = os.getenv("BOT_API", "http://localhost:8000/post")

def send_to_miniapp(chat_title, message_text, message_link=None):
    payload = {
        "chat_title": chat_title,
        "text": message_text,
        "link": message_link,
    }
    try:
        r = requests.post(BOT_API, json=payload, timeout=5)
        if r.status_code != 200:
            log.warning("miniapp returned %s: %s", r.status_code, r.text)
    except Exception as e:
        log.exception("Не удалось отправить в мини-апп: %s", e)
