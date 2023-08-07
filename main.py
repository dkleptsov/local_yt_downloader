import os
import re
import csv
import yt_dlp
from pprint import pprint
import channel_db
import env
# from pytube import YouTube


def download_mp4(url:str, path:str=env.VIDEOS_PATH) -> None:
    ydl_opts = {"verbose":True,
                "format": "mp4[height=1080]", 
                # "format":"bestvideo/best",
                'outtmpl':path + '%(title)s.%(ext)s',}
    # while True:
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(e)


def download_mp3(url:str, path:str=env.AUDIOS_PATH) -> None:
    ydl_opts = {"verbose":True,
                "format": "bestaudio/best",
                "extractaudio": True,
                "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",}],
                'outtmpl':path + '%(title)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def get_channel_path(url:str):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            channel_name = video_info.get('channel')
            if not channel_name:
                channel_name = video_info.get('uploader')
            return f"{env.VIDEOS_PATH}{filter_unsafe_names(channel_name)}/"
    except yt_dlp.DownloadError:
        return None


def filter_unsafe_names(name:str):
    unsafe_pattern = r'[^A-Za-zА-Яа-я_\- ]'
    filtered_text = re.sub(unsafe_pattern, '', name)
    return filtered_text[:100]


def get_all_channel_videos(channel_url:str, type:str):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(channel_url, download=False)
            channel_url = channel_info["uploader_url"]
            # Нужен ли вообще этот токен?
            videos = []
            next_page_token = None

            while True:
                playlist_url = f"{channel_url}/{type}"
                if next_page_token:
                    playlist_url += f"&page_token={next_page_token}"

                playlist_info = ydl.extract_info(playlist_url, download=False)
                playlist_videos = playlist_info['entries']
                videos.extend(playlist_videos)

                next_page_token = playlist_info.get('nextpage')

                if not next_page_token:
                    break

            return videos
    except yt_dlp.DownloadError as e:
        print(f"Error: {e}")
        return None


def create_channel_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except OSError as e:
            print(f"Error: {e}")
    else:
        print(f"Folder '{folder_path}' already exists.")


def save_data_to_csv(data:list,path:str):

    keys = data[0].keys() #["url","title","ie_key","duration"]

    with open(f"{path}db.csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def create_channel_db(url:str):
    channel_path = get_channel_path(url)
    create_channel_folder(channel_path)
    pprint(get_all_channel_videos(url, "videos")[-1])
    print("*"*80)
    short_info = get_all_channel_videos(url, "shorts")
    pprint(short_info[-1])
    save_data_to_csv(short_info,channel_path)


def main():
    # # Test the function
    # channel_url = "https://www.youtube.com/user/ExampleChannel"
    # videos = get_all_channel_videos(channel_url)

    # if videos:
    #     for video in videos:
    #         print(f"Video Title: {video['title']}, Video ID: {video['id']}")

    # download_mp4(TEST_SHORTS)
    # download_mp3(TEST_SHORTS)
    # channel_videos = get_all_channel_videos(TEST_SHORTS)
    # pprint(channel_videos)
    # print(len(channel_videos))
    create_channel_db(env.TEST_SHORTS)


if __name__ == "__main__":
    main()


# --> TODO: Create folders with name of channel and put videos there
# TODO: Избавиться от циклического скачивания ютуб шортс
# TODO: Instagram shorts?
# TODO: List from a file