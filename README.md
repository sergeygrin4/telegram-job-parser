# Telegram Job Parser + Mini App (Railway)

Два сервиса:
- **miniapp (web)** — HTTP `/post` принимает JSON и отправляет сообщение менеджеру через Telegram-бота.
- **parser (worker)** — слушает каналы в Telegram и постит найденные сообщения в miniapp.

## Быстрый старт локально

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env  # и заполнить
python mini_app_bot.py  # web
# в другой вкладке
python telegram_parser.py  # worker

Тестовый POST:

curl -X POST http://localhost:8000/post \
 -H "Content-Type: application/json" \
 -H "X-SECRET: $SHARED_SECRET" \
 -d '{"chat_title":"Канал вакансий","text":"Python dev, удалённо","link":"https://t.me/some/1"}'
