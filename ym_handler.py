from config import YM_TOKEN
from yandex_music import Client

client = Client(YM_TOKEN)
client.init()


def search_artist(query):
    search_result = client.search(query)

    if not search_result.best or search_result.best.type != "artist":
        return None

    artist = search_result.best.result
    return {
        "id": artist.id,
        "name": artist.name,
        "url": f"https://music.yandex.ru/artist/{artist.id}",
    }
