import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import API_TOKEN
from DB import init_db

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()

# Логирование исключений
@dp.errors_handler(exception=Exception)
async def global_error_handler(update, exception):
    logger.exception(f'Update: {update} \n{exception}')
    return True

if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)
