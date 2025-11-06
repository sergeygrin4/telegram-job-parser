# Telegram Job Parser + Mini App (Railway)

Два сервиса:
- **miniapp (web)** — HTTP `/post` принимает JSON и отправляет сообщение менеджеру через Telegram-бота.
- **parser (worker)** — слушает каналы в Telegram и постит найденные сообщения в miniapp.

## Быстрый старт локально

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env  # и заполнить
python mini_app_bot.py  # web
# в другой вкладке
python telegram_parser.py  # worker
