import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from app.config import config

# Настройка логов [cite: 42]
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher()

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    """Автоматическая установка Webhook при старте [cite: 91]"""
    webhook_url = f"{config.BASE_URL}{config.WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook_url)
    logging.info(f"Webhook set to: {webhook_url}")

@app.on_event("shutdown")
async def on_shutdown():
    """Удаление Webhook при выключении"""
    await bot.delete_webhook()
    await bot.session.close()

@app.post(config.WEBHOOK_PATH)
async def bot_webhook(request: Request):
    """Эндпоинт для обновлений от Telegram [cite: 98]"""
    update = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса [cite: 99]"""
    return {"status": "healthy"}