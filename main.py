import os
import subprocess
import yt_dlp
import sys
import re
import requests
import random

# Функция для получения списка прокси-серверов
def get_proxy_list():
    proxy_api_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    response = requests.get(proxy_api_url)
    return response.text.splitlines()

# Функция случайного выбора прокси-сервера из списка
def get_random_proxy(proxy_list):
    return random.choice(proxy_list)

# Функция проверки прокси-сервера
def check_proxy(proxy_url):
    try:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        response = requests.get("http://www.google.com", proxies=proxies, timeout=10, verify=False)
        if response.status_code == 200:
            print("Прокси работает")
        else:
            print("Прокси не работает, статус:", response.status_code)
            sys.exit()
    except Exception as e:
        print("Ошибка подключения к прокси:", str(e))
        sys.exit()

def sanitize_filename(filename):
    """Удаляет недопустимые символы из имени файла для Windows"""
    return re.sub(r'[<>:"/\|?*]', '', filename)

def download_and_play_youtube_video(search_term, by_url, advanced_search=False):
    proxy_list = get_proxy_list()
    proxy_url = get_random_proxy(proxy_list)  # Получаем случайный прокси URL
    print(f"Используемый прокси-сервер: {proxy_url}")
    check_proxy(proxy_url)  # Проверяем прокси
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',  # Сохраняем видео в текущей директории
        'proxy': proxy_url,
        'nocheckcertificate': True,  # Отключение проверки сертификатов
    }
    video_url = None
    video_title = None

    if advanced_search:
        query = f"ytsearch10:{search_term}"
        with yt_dlp.YoutubeDL({'quiet': True, 'proxy': proxy_url}) as ydl:
            try:
                result = ydl.extract_info(query, download=False)
            except yt_dlp.utils.DownloadError as e:
                print(f"Ошибка при разборе JSON: {str(e)}")
                return

            if result and 'entries' in result:
                while True:
                    print("Введите цифру для выбора видео или 11 для загрузки ещё 10 видео:")
                    for idx, entry in enumerate(result['entries'], start=1):
                        print(f"{idx}) {entry['title']} | {entry['uploader']} | {entry['duration'] // 60}мин {entry['duration'] % 60}сек")

                    print("11) Загрузить остальные 10 видео из поиска")
                    choice = input("Ваш выбор: ")
                    if choice.isdigit() and int(choice) in range(1, 12):
                        choice = int(choice)
                        if choice == 11:
                            if 'continuation' in result:
                                result = ydl.extract_info(f"ytsearch10:{search_term}&sp={result['continuation']}", download=False)
                            else:
                                print("Больше нет видео для загрузки.")
                                return
                        else:
                            video_url = result['entries'][choice - 1].get('url')
                            video_title = result['entries'][choice - 1].get('title')
                            break
                    else:
                        print("Неверный выбор. Попробуйте снова.")
            else:
                print("Видео не найдено по запросу. Попробуйте снова.")
                return
    else:
        if by_url:
            video_url = search_term
        else:
            query = f"ytsearch:{search_term}"
            with yt_dlp.YoutubeDL({'quiet': True, 'proxy': proxy_url}) as ydl:
                try:
                    result = ydl.extract_info(query, download=False)
                except yt_dlp.utils.DownloadError as e:
                    print(f"Ошибка при разборе JSON: {str(e)}")
                    return
                if result and 'entries' in result:
                    entry = result['entries'][0] if result['entries'] else {}
                    video_url = entry.get('url')
                    video_title = entry.get('title')
                if not video_url or not video_title:
                    print("Видео не найдено по запросу. Попробуйте снова.")
                    return

    # Использование yt-dlp для загрузки видео
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Поиск имени загруженного файла
    downloaded_file = None
    for file in os.listdir('.'):
        if file.startswith('downloaded_video'):
            downloaded_file = file
            break

    if not downloaded_file:
        print("Скачивание видео не удалось!")
        return

    # Переименование файла видео в соответствие с названием видео
    file_extension = downloaded_file.split('.')[-1]
    new_file_name = f"{sanitize_filename(video_title)}.{file_extension}"
    os.rename(downloaded_file, new_file_name)

    # Воспроизведение видео с помощью стандартного видеоплеера
    if os.name == 'nt':  # Windows
        os.startfile(new_file_name)
    elif os.name == 'posix':  # macOS и Linux
        subprocess.call(('open', new_file_name) if sys.platform == 'darwin' else ('xdg-open', new_file_name))

    # Ожидает завершения просмотра видео, затем удаляет файл
    input("Press Enter after you finish watching the video...")
    os.remove(new_file_name)

# Главный скрипт
def main():
    os.system("yt-dlp -U")  # Команда для обновления yt-dlp
    print("Напишите 1 чтобы найти видео с помощью поиска")
    print("Напишите 2 чтобы найти видео с помощью URL")
    print("Напишите 3 чтобы использовать продвинутый поиск (рекомендуется)")
    []
    choice = input("Ваш выбор: ")

    if choice == '1':
        search_term = input("Введите название видео для поиска: ")
        download_and_play_youtube_video(search_term, by_url=False)
    elif choice == '2':
        video_url = input("Введите URL видео: ")
        download_and_play_youtube_video(video_url, by_url=True)
    elif choice == '3':
        search_term = input("Введите запрос для продвинутого поиска: ")
        download_and_play_youtube_video(search_term, by_url=False, advanced_search=True)
    else:
        print("Неверный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    main()