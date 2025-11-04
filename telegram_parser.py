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

# Отправляем то же сообщение в мини-апп-бота
import requests
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = MANAGER_ID  # можно отправлять самому менеджеру или в общий чат
BOT_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": f"/vacancy {chat_title}|{message_link}|{message_text}",
}
try:
    requests.post(BOT_API, json=payload)
except Exception as e:
    log.warning("Не удалось отправить в мини-апп: %s", e)


async def main():
    await client.start()
    log.info("👂 Парсер запущен и слушает чаты...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
