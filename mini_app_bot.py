import logging, os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("7952407611:AAF_J8xFIE4FEL5Kmf6cFMUL0BZaEQsn_7s")
bot = Bot(BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# хэндлер для теста
@dp.message(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("👋 Бот готов принимать посты от парсера.")

# хэндлер для приёма новых вакансий (будет слать Telethon-парсер)
@dp.message(commands=["vacancy"])
async def vacancy(msg: types.Message):
    # формат: /vacancy <chat_title>|<link>|<text>
    try:
        data = msg.text.split(" ", 1)[1]
        chat_title, link, text = data.split("|", 2)
    except Exception:
        await msg.answer("❌ Неверный формат.")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="🔎 Проверить", url=link)
    await msg.answer(
        f"📢 *{chat_title}*\n\n{text.strip()}\n",
        reply_markup=kb.as_markup(),
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
