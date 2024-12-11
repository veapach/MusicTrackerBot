from config import YM_TOKEN
from yandex_music import Client

client = Client(YM_TOKEN)
client.init()

type_to_name = {
    "track": "трек",
    "artist": "исполнитель",
    "album": "альбом",
    "playlist": "плейлист",
    "video": "видео",
    "user": "пользователь",
    "podcast": "подкаст",
    "podcast_episode": "эпизод подкаста",
}


def search(query):
    search_result = client.search(query)

    text = [f'Результаты по запросу "{query}":', ""]

    best_result_text = ""
    if search_result.best:
        type_ = search_result.best.type
        best = search_result.best.result

        text.append(f"❗️Лучший результат: {type_to_name.get(type_)}")

        if type_ in ["track", "podcast_episode"]:
            artists = ""
            if best.artists:
                artists = " " + ", ".join(artist.name for artist in best.artists)

            album = best.albums[0].id

            best_result_text = f"{artists} - {best.title}\nСсылка - https://music.yandex.ru/album/{album}/track/{best.id}"

        elif type_ == "artist":
            best_result_text = (
                f"{best.name}\nСсылка - https://music.yandex.ru/artist/{best.id}"
            )
        elif type_ in ["album", "podcast"]:
            best_result_text = best.title
        elif type_ == "playlist":
            best_result_text = best.title
        elif type_ == "video":
            best_result_text = f"{best.title} {best.text}"

        text.append(f"Содержимое лучшего результата: {best_result_text}\n")

        text.append("")
        return "\n".join(text)
