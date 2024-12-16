import asyncio
from aiogram import Bot
from db import session, Artist, Subscription, User
from ym_handler import client
from datetime import datetime
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def test_notifications(bot):
    # Получаем все подписки
    subscriptions = session.query(Subscription).all()

    for subscription in subscriptions:
        user_id = subscription.user_id
        artist = session.query(Artist).filter_by(id=subscription.artist_id).first()

        if not artist:
            continue

        # Проверяем информацию об артисте (например, релизы)
        ym_artists = client.artists(artist.id)
        if not ym_artists:
            continue

        ym_artist = ym_artists[0]

        # Тестовое уведомление о релизе
        test_message = (
            f"Тестовое уведомление: {ym_artist.name} выпустил(а) новый релиз!"
        )
        await bot.send_message(user_id, test_message)


async def check_new_releases():
    artists = session.query(Artist).all()
    for artist in artists:
        # Получаем данные артиста из API
        ym_artist = client.artists(artist.id)
        new_releases = [
            album
            for album in ym_artist.albums
            if album.release_date
            and album.release_date > (artist.last_release_date or datetime.min)
        ]

        if new_releases:
            # Обновляем дату последнего релиза
            latest_release_date = max(album.release_date for album in new_releases)
            artist.last_release_date = latest_release_date
            session.commit()

            # Уведомляем подписчиков
            subscriptions = (
                session.query(Subscription).filter_by(artist_id=artist.id).all()
            )
            for sub in subscriptions:
                user = session.query(User).filter_by(id=sub.user_id).first()
                await send_notification(user.id, artist.name, new_releases)


async def send_notification(user_id, artist_name, releases):
    release_titles = ", ".join([release.title for release in releases])
    await bot.send_message(
        chat_id=user_id, text=f"У {artist_name} новый релиз: {release_titles}"
    )


# Планировщик для проверки
async def scheduler():
    while True:
        await check_new_releases()
        await asyncio.sleep(3600)  # Проверять раз в час


if __name__ == "__main__":
    asyncio.run(scheduler())
