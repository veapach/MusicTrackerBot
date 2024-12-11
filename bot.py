import asyncio
from config import BOT_TOKEN
import ym_handler
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f"Ку, я выполняю поиск по Яндекс Музыке. \nНапиши свой запрос")


@dp.message()
async def search(message: Message):
    result = ym_handler.search(message.text)
    await message.answer(result)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


asyncio.run(main())
