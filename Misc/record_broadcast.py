#!/usr/bin/python3

import subprocess
from github import Github
from datetime import datetime
import requests

def delete_old_files(repo, path, max_files):
    contents = repo.get_contents(path)
    if len(contents) > max_files:
        sorted_files = sorted(contents, key=lambda x: x.last_modified)
        for file_to_delete in sorted_files[:len(contents) - max_files]:
            repo.delete_file(file_to_delete.path, "Deleted old file", file_to_delete.sha)

def record_newscast(channel_name, channel_link):

    now = datetime.now()
    time = now.strftime('%Y-%m-%d-%H%M')

    yt_dlp_command = [
        'yt-dlp',
        '-g',
        f'{channel_link}'
    ]

    result = subprocess.run(yt_dlp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        m3u8_url = result.stdout.strip()

    response = requests.get(m3u8_url)

    if response.status_code == 200:

        audio_file_path = f'/home/casey/Downloads/{channel_name}_{time}.aac'
        audio_file = f"{channel_name}_{time}.aac"

        print(f"Recording audio: {audio_file}")

        command = [
            'ffmpeg',
            '-i', m3u8_url,
            '-t', '960',
            '-bsf:a', "aac_adtstoasc",
            '-b:a', '192k',
            audio_file_path
        ]

        result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
        error = result.stderr

        if result.returncode != 0:
            print(error)
            with open(f'/home/casey/Downloads/{channel_name}_{time}.txt', 'w') as file:
                file.write(f"Error occured.\n{error}")
        else:
            print("Uploading to GitHub")

            g = Github("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")

            repo = g.get_user().get_repo("spanish-app")
            with open(audio_file_path, 'rb') as file:
                audio_content = file.read()
                repo.create_file(f"Newscasts/{audio_file}", "new newscast", audio_content)

            print("File uploaded.")
            delete_old_files(repo, "Newscasts", 6)
    else:
        with open(f'/home/casey/Downloads/{channel_name}_{time}.txt', 'w') as file:
            file.write(f"Error occured: {str(response.status_code)}")

f24_name = "France_24_Español"
f24_link = "https://www.youtube.com/watch?v=Y-IlMeCCtIg"

record_newscast(f24_name, f24_link)