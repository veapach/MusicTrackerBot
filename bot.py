import asyncio
from config import BOT_TOKEN
import ym_handler
from ym_handler import client
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from db import session, User, Artist, Subscription
from datetime import datetime
from release_checker import test_notifications

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f"Ку, я выполняю поиск по Яндекс Музыке. \nНапиши свой запрос")


@dp.message(Command("test_notification"))
async def send_test_notifications(message: Message, bot: Bot):
    await test_notifications(bot)
    await message.answer("Тестовые уведомления отправлены!")


@dp.message()
async def search_artist_handler(message: Message):
    query = message.text
    artist = ym_handler.search_artist(query)

    if artist:
        # Проверяем, подписан ли пользователь на артиста
        user_id = message.from_user.id
        subscription = (
            session.query(Subscription)
            .filter_by(user_id=user_id, artist_id=artist["id"])
            .first()
        )
        button_text = "Отписаться" if subscription else "Подписаться"
        callback_data = (
            f"{'unsubscribe' if subscription else 'subscribe'}:{artist['id']}"
        )

        # Отправляем сообщение с кнопкой
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=button_text, callback_data=callback_data)]
            ]
        )
        await message.answer(
            f"{artist['name']}\n[Перейти к артисту]({artist['url']})",
            reply_markup=keyboard,
        )
    else:
        await message.answer("Артист не найден.")


@dp.callback_query(lambda c: c.data.startswith("subscribe"))
async def subscribe_to_artist(callback: CallbackQuery):
    artist_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    # Получаем информацию об артисте
    ym_artists = client.artists(artist_id)
    if not ym_artists:
        await callback.answer("Артист не найден", show_alert=True)
        return

    ym_artist = ym_artists[0]  # Берём первого артиста из результата

    # Добавляем артиста в базу, если его ещё нет
    artist = session.query(Artist).filter_by(id=artist_id).first()
    if not artist:
        artist = Artist(id=artist_id, name=ym_artist.name)
        session.add(artist)

    # Добавляем пользователя в базу, если его ещё нет
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id, username=callback.from_user.username)
        session.add(user)

    # Создаём подписку
    subscription = (
        session.query(Subscription)
        .filter_by(user_id=user.id, artist_id=artist.id)
        .first()
    )
    if not subscription:
        subscription = Subscription(user_id=user.id, artist_id=artist.id)
        session.add(subscription)
        session.commit()

    await callback.message.edit_text(f"Вы подписались на {artist.name}.")
    await callback.answer()


# Отписка от артиста
@dp.callback_query(lambda c: c.data.startswith("unsubscribe"))
async def unsubscribe_from_artist(callback: CallbackQuery):
    artist_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    # Удаляем подписку
    subscription = (
        session.query(Subscription)
        .filter_by(user_id=user_id, artist_id=artist_id)
        .first()
    )
    if subscription:
        session.delete(subscription)
        session.commit()

    # Обновляем сообщение
    artist = session.query(Artist).filter_by(id=artist_id).first()
    await callback.message.edit_text(f"Вы отписались от {artist.name}.")
    await callback.answer()


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


asyncio.run(main())
