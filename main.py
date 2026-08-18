import asyncio
import logging
import sys

from maxapi import Bot, Dispatcher

import config
from database import db
from scheduler import setup_scheduler, start_scheduler, stop_scheduler

from handlers.all_handlers import dp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    logger.info("🚀 Бот ЗОЖник запускается...")
    
    await db.init()
    logger.info("✅ База данных инициализирована")
    
    setup_scheduler(bot)
    start_scheduler()
    
    logger.info("✅ Бот готов к работе!")


async def on_shutdown(bot: Bot):
    logger.info("🛑 Остановка бота...")
    stop_scheduler()
    await db.close()
    logger.info("✅ Бот остановлен")


async def main():
    bot = Bot(token=config.MAX_BOT_TOKEN)
    
    await on_startup(bot)
    
    try:
        logger.info("▶️ Запуск в режиме polling...")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Получен сигнал остановки")
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    asyncio.run(main())