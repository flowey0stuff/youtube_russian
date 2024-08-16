import os
import subprocess
import yt_dlp
import sys
import urllib.parse

def download_and_play_youtube_video(search_term, by_url, advanced_search=False):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloaded_video.%(ext)s',  # Save the video in the current directory
    }
    video_url = None
    video_title = None

    if advanced_search:
        query = f"ytsearch10:{search_term}"
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            result = ydl.extract_info(query, download=False)
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
                            result = ydl.extract_info(f"ytsearch10:{search_term}&sp={result['continuation']}", download=False)
                            continue
                        else:
                            video_url = result['entries'][choice - 1]['url']
                            video_title = result['entries'][choice - 1]['title']
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
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                result = ydl.extract_info(query, download=False)
                if result and 'entries' in result:
                    video_url = result['entries'][0]['url']
                    video_title = result['entries'][0]['title']
                else:
                    print("Видео на найдено по запросу. Попробуйте снова.")
                    return

    # Using yt-dlp to download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Find the downloaded file name
    downloaded_file = None
    for file in os.listdir('.'):
        if file.startswith('downloaded_video'):
            downloaded_file = file
            break

    if not downloaded_file:
        print("Скачивание видео не удалось!")
        return

    # Rename the video file to the video title
    file_extension = downloaded_file.split('.')[-1]
    new_file_name = f"{video_title}.{file_extension}"
    os.rename(downloaded_file, new_file_name)

    # Playing the video with the default video player
    if os.name == 'nt':  # Windows
        os.startfile(new_file_name)
    elif os.name == 'posix':  # macOS and Linux
        subprocess.call(('open', new_file_name) if sys.platform == 'darwin' else ('xdg-open', new_file_name))

    # Wait for video to finish playing then delete it
    input("Press Enter after you finish watching the video...")
    os.remove(new_file_name)

# Main script
def main():
    print("Напишите 1 чтобы найти видео с помощью поиска")
    print("Напишите 2 чтобы найти видео с помощью URL")
    print("Напишите 3 чтобы использовать продвинутый поиск (рекомендуется)")
    choice = input("Ваш выбор: ")

    if choice == '1':
        search_term = input("Введите название видео для поиска: ")
        download_and_play_youtube_video(search_term, by_url=False)
    elif choice == '2':
        video_url = input("Введите URL видео: ")
        download_and_play_youtube_video(video_url, by_url=True)
    elif choice == '3':
        []
        search_term = input("Введите запрос для продвинутого поиска: ")
        download_and_play_youtube_video(search_term, by_url=False, advanced_search=True)
    else:
        print("Неверный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    main()