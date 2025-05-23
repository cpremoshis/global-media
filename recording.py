import streamlit as st
import requests
import time
from datetime import datetime
import subprocess
from tqdm import tqdm
import ffmpeg
from io import BytesIO
import openai
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
    
#    m3u8_url = "https://live-hls-web-aje-fa.getaj.net/AJE/02.m3u8"
#    root_url = "https://live-hls-web-aje-fa.getaj.net/AJE/"
#    output_file = "/Users/casey/Downloads/CONCAT TEST.mp4"
#    output_file = "./Recordings/CONCAT TEST.mp4"

#Removes potential duplicates in the 'files_list'
def remove_duplciates(files_list):
    return list(dict.fromkeys(files_list))

def translate_audio(video_file, outlet, savetime):
    try:
        openai.api_key = st.secrets['openai_key']
        
        if video_file.endswith(".mp3") == True:
            audio_file = video_file
        else:
            audio_file = f"./Recordings/{outlet}_{savetime}.mp3"

            input_file = ffmpeg.input(video_file)
            input_file.output(audio_file, acodec="mp3").run()

        # Read the audio file into a BytesIO object
        with open(audio_file, 'rb') as f:
            audio_bytes = BytesIO(f.read())
            audio_bytes.name = "audio.mp3"

        translation = openai.audio.translations.create(
            file = audio_bytes,
            model='whisper-1',
            response_format="srt"
        )

        translation_file = f"./Recordings/{outlet}_{savetime}.srt"

        with open(translation_file, 'w') as file:
            file.write(translation)

        return translation_file, audio_file
    except Exception as e:
        return e

#Enter seconds in intervals of FIVE
def record_m3u8(outlet, seconds, playlist_url, root_url, translate):

    try:

        now = datetime.now()
        savetime = now.strftime("%Y_%m_%d_%H%M%S")

        files_list = []

        text = requests.get(playlist_url)
        lines = text.text.splitlines()

        #.ts files
        try:
            #List of .ts files in M3U8 file
            ts_files = [line for line in lines if ".ts" in line]

            #Adds any .ts file to "files_list" if that .ts file is not already present
            if root_url != "Null":
                for item in ts_files:
                    if root_url + item not in files_list:
                        files_list.append(root_url + item)
            #This block is for RTVE, BBC TV
            else:
                for item in ts_files:
                    if item not in files_list:
                        files_list.append(item)

            #This is the .ts file that SHOULD most closely corresponds to the time when user began recording
            record_start = files_list[-3]

            #Removes potential duplicates in the 'files_list'
            files_list = remove_duplciates(files_list)

            cycles = seconds / 5

            #Reloads M3U8 playlist every 5 seconds, adding new .ts files to 'files_list'
            for number in tqdm(range(int(cycles)), desc="Logging .ts files"):

                text = requests.get(playlist_url)

                lines = text.text.splitlines()

                ts_files = [line for line in lines if ".ts" in line]

                if root_url != "Null":
                    for item in ts_files:
                        if root_url + item not in files_list:
                            files_list.append(root_url + item)
                #This block is for RTVE, BBC TV
                else:
                    for item in ts_files:
                        if item not in files_list:
                            files_list.append(item)

                time.sleep(5)

            media_type = "ts"

        #.aac files
        except:
            #List of .aac files in M3U8 file
            aac_files = [line for line in lines if line.endswith(".aac")]

            #Adds any .aac file to "files_list" if that .aac file is not already present
            for item in aac_files:
                if root_url + item not in files_list:
                    files_list.append(root_url + item)

            #This is the .aac file that most closely corresponds to the time when user began recording
            record_start = files_list[-2]

            #Removes potential duplicates in the 'files_list'
            files_list = remove_duplciates(files_list)

            cycles = seconds / 5

            #Reloads M3U8 playlist every 5 seconds, adding new .aac files to 'files_list'
            for number in tqdm(range(int(cycles)), desc="Logging .aac files"):

                text = requests.get(playlist_url)

                lines = text.text.splitlines()

                aac_files = [line for line in lines if line.endswith(".aac")]

                for item in aac_files:
                    if root_url + item not in files_list:
                        files_list.append(root_url + item)

                time.sleep(5)

            media_type = "aac"

        #Creates a new list only with the "record_start" .ts file and those AFTER it
        record_start_index = files_list.index(record_start)
        files_list_final = files_list[record_start_index:]

        #Starting string that will be added to and eventually fed to ffmpeg
        concat_string = "concat:"

        #The only difference between the "if" and "else" is that the "else" block does not add a "|" after the file name,
        #as the last file in the list must end with ."ts" not ".ts|"
        for number in tqdm(range(0, len(files_list_final)), f"Saving {media_type} files"):
            if number != len(files_list_final) - 1:
        
                item = files_list_final[number]

#                file_path = f"/Users/casey/Downloads/ts_file_{number}.{media_type}"
                file_path = f"./Recordings/{outlet}_{savetime}_ts_file_{number}.{media_type}"

                response = requests.get(item)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    concat_string = concat_string + file_path + "|"
                else:
                    pass
            
            else:
                item = files_list_final[number]

#                file_path = f"/Users/casey/Downloads/ts_file_{number}.{media_type}"
                file_path = f"./Recordings/{outlet}_{savetime}_ts_file_{number}.{media_type}"

                response = requests.get(item)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    concat_string = concat_string + file_path
                else:
                    pass

        output_file = f"./Recordings/{outlet}_{savetime}.mp4"

        #Combines .ts files using 'ffmpeg'
        if media_type == "ts":
            command = [
                'ffmpeg',
                '-i', concat_string,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_file
            ]

            subprocess.run(command)

            if translate == True:
                #TRANSLATION command
                translation_file, audio_file = translate_audio(output_file, outlet, savetime)

                # Add subtitle file to the mp4
                subtitle_command = [
                    'ffmpeg',
                    '-y',
                    '-i', output_file,
                    '-i', translation_file,  # This is the SRT file
                    '-c', 'copy',
                    '-c:s', 'mov_text',  # This ensures the subtitle codec is compatible with MP4
                    '-metadata:s:s:0', 'language=eng',  # Change 'eng' to the appropriate language code
                    output_file  # This is the output file with subtitles
                ]

                subprocess.run(subtitle_command)

                return True, outlet, output_file, translation_file, audio_file
            
            else:
                return True, outlet, output_file

        #Combines .aac files using 'ffmpeg'
        elif media_type == "aac":
            command = [
                'ffmpeg',
                '-i', concat_string,
                '-c:a', 'copy',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_file
            ]

            subprocess.run(command)

            if translate == True:
                #TRANSLATION command
                translation_file, audio_file = translate_audio(output_file, outlet, savetime)

                return True, outlet, output_file, translation_file, audio_file
            
            else:
                return True, outlet, output_file

    except Exception as e:

        return False, e

def record_mpd(outlet, seconds, stream_url, translate):

    now = datetime.now()
    savetime = now.strftime("%Y_%m_%d_%H%M%S")

    save_file = f"./Recordings/{outlet}_{savetime}.ts"
    output_file = f"./Recordings/{outlet}_{savetime}.mp4"

    save_command = [
        'timeout', str(seconds),
        'streamlink',
        stream_url,
        'best',
        '-o', save_file
        ]

    convert_command = [
        'ffmpeg',
        '-i', save_file,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_file
        ]

    result = subprocess.run(save_command)
    subprocess.run(convert_command)

######
######
#NEED TO FIX EDITING IN PLACE ERROR WITH FFMPEG WHEN ADDING SUBTITLES

    if translate == True:
        #TRANSLATION command
        translation_file, audio_file = translate_audio(output_file, outlet, savetime)

        # Add subtitle file to the mp4
        subtitle_command = [
            'ffmpeg',
            '-y',
            '-i', output_file,
            '-i', translation_file,  #SRT file
            '-c', 'copy',
            '-c:s', 'mov_text',  #Subtitle codec compatible with MP4
            '-metadata:s:s:0', 'language=eng',  #Change 'eng' to the appropriate language code if other than English
            output_file  #Output file with subtitles
        ]

        subprocess.run(subtitle_command)

        return True, outlet, output_file, translation_file, audio_file
    else:
        return True, outlet, output_file

#Enter seconds in intervals of FIVE
def record_youtube(outlet, seconds, stream_url, translate):
    try:

        now = datetime.now()
        savetime = now.strftime("%Y_%m_%d_%H%M%S")

        yt_dlp_command = [
            'yt-dlp',
            '-g',
            f'{stream_url}'
        ]

        result = subprocess.run(yt_dlp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            m3u8_url = result.stdout.strip()
 
        files_list = []

        text = requests.get(m3u8_url)
        lines = text.text.splitlines()

        #List of .ts files in M3U8 file
        ts_files = [line for line in lines if line.endswith(".ts")]

        #Adds any .ts file to "files_list" if that .ts file is not already present
        for item in ts_files:
            if item not in files_list:
                files_list.append(item)

        #This is the .ts file that most closely corresponds to the time when user began recording
        record_start = files_list[-2]

        #Removes potential duplicates in the 'files_list'
        files_list = remove_duplciates(files_list)

        cycles = seconds / 5

        #Reloads M3U8 playlist every 5 seconds, adding new .ts files to 'files_list'
        for number in tqdm(range(int(cycles)), desc="Logging .ts files"):

            text = requests.get(m3u8_url)

            lines = text.text.splitlines()

            ts_files = [line for line in lines if line.endswith(".ts")]

            for item in ts_files:
                if item not in files_list:
                    files_list.append(item)

            time.sleep(5)

        media_type = "ts"

        #Creates a new list only with the "record_start" .ts file and those AFTER it
        record_start_index = files_list.index(record_start)
        files_list_final = files_list[record_start_index:]

        #Starting string that will be added to and eventually fed to ffmpeg
        concat_string = "concat:"

        #The only difference between the "if" and "else" is that the "else" block does not add a "|" after the file name,
        #as the last file in the list must end with ."ts" not ".ts|"
        for number in tqdm(range(0, len(files_list_final)), f"Saving {media_type} files"):
            if number != len(files_list_final) - 1:
        
                item = files_list_final[number]

#                file_path = f"/Users/casey/Downloads/ts_file_{number}.{media_type}"
                file_path = f"./Recordings/{outlet}_{savetime}_ts_file_{number}.{media_type}"

                response = requests.get(item)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    concat_string = concat_string + file_path + "|"
                else:
                    pass
            
            else:
                item = files_list_final[number]

#                file_path = f"/Users/casey/Downloads/ts_file_{number}.{media_type}"
                file_path = f"./Recordings/{outlet}_{savetime}_ts_file_{number}.{media_type}"

                response = requests.get(item)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    concat_string = concat_string + file_path
                else:
                    pass

        output_file = f"./Recordings/{outlet}_{savetime}.mp4"

        #Combines .ts files using 'ffmpeg'
        command = [
            'ffmpeg',
            '-i', concat_string,
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_file
        ]

        subprocess.run(command)

        if translate == True:
            #TRANSLATION command
            translation_file, audio_file = translate_audio(output_file, outlet, savetime)

            return True, outlet, output_file, translation_file, audio_file
        
        else:
            return True, outlet, output_file

    except Exception as e:
        return False, e

#Enter seconds in intervals of FIVE
def record_mp3(outlet, seconds, stream_url, translate):

    try:
        now = datetime.now()
        savetime = now.strftime("%Y_%m_%d_%H%M%S")

        response = requests.get(stream_url, stream=True)

        start_time = time.time()

        output_file = f"./Recordings/{outlet}_{savetime}.mp3"

        with open(output_file, 'wb') as f:
            for block in response.iter_content(1024):
                elapsed_time = time.time() - start_time

                if elapsed_time > seconds:
                    break
                f.write(block)
        
        response.close()

        if translate == True:
            #TRANSLATION command
            translation_file, audio_file = translate_audio(output_file, outlet, savetime)

            return True, output_file, translation_file, audio_file
        
        else:
            return True, output_file
    
    except Exception as e:
        
        return False, e

def multi_record(*outlets, seconds, translate=False):

    try:

        now = datetime.now()
        savetime = now.strftime("%Y_%m_%d_%H%M%S")

        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:

            # Dictionary to hold future to outlet mapping
            future_to_outlet = {}
            
            for outlet in outlets:
                if outlet.format == "M3U8":
                    future = executor.submit(record_m3u8, outlet.name, seconds, outlet.recording_url, outlet.root_url, translate)
                if outlet.format == "MPD":
                    future = executor.submit(record_mpd, outlet.name, seconds, outlet.recording_url, translate)
                if outlet.format == "YouTube":
                    future = executor.submit(record_youtube, outlet.name, seconds, outlet.recording_url, translate)
                future_to_outlet[future] = outlet

            # Dictionary to hold future to outlet mapping
            #future_to_outlet = {
            #    executor.submit(record_m3u8, outlet.name, seconds, outlet.recording_url, outlet.root_url, translate): outlet
            #    for outlet in outlets
            #}

            results = []
            for future in as_completed(future_to_outlet):
                try:
                    # Get the result from the future
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"{future_to_outlet[future].name} generated an exception: {exc}")
                    
        video_dict = {}

        if len(results[0]) == 3:

            for item in results:
                if item[0] == True:
                    video_dict[item[1]] = {"Video":item[2], "Subtitles":"None"}

            return True, video_dict, savetime
    
        if len(results[0]) == 5:

            for item in results:
                if item[0] == True:
                    video_dict[item[1]] = {"Video":item[2], "Subtitles":item[3], "Audio":item[4]}

        return True, video_dict, savetime

    except Exception as e:
        return e
    
def download_from_webpages(link, translate):

    #NEED TO ADD AUTO DELETION OF TEMP FILES
    #ADD TRANSLATION OPTION
    try:

        if 'youtube.com' in link or 'youtu.be' in link:
            link_lower = link.strip()
        else:
            link_lower = link.lower().strip()

        source_types_dict = {
            'youtube.com':'YouTube',
            'youtu.be':'YouTube',
            'instagram.com':'Instagram',
            'x.com':'X',
            'facebook.com':'Facebook',
            'fb.watch':'Facebook',
            't.me':'Telegram'
            }
        
        source_type = 'unknown_source'

        for key, value in source_types_dict.items():
            if key in link_lower:
                source_type = value
                break                

        #Gets date and time
        now = datetime.now()
        savetime = now.strftime("%d_%m__%Y_%H%M%S")

        #Gets account name for use in file name
        extract_uploader_name_command = [
            'yt-dlp',
            '--print',
            '%(uploader)s',
            link_lower
            ]
        uploader_name = subprocess.check_output(extract_uploader_name_command, text=True).strip().replace(" ", "_")

        #Output file name and location
        download_file_path = f'/mount/src/global-media/Recordings/{source_type}_{uploader_name}_{savetime}.mp4'
        converted_file_path = None

        if source_type == "YouTube":
            download_command = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]',
                '-o', download_file_path,
                link_lower
                ]
        else:
            download_command = [
                'yt-dlp',
                '--cookies', '/mount/src/global-media/Assets/all_cookies.txt',
                '-o', download_file_path,
                link_lower
                ]
        
        subprocess.run(download_command, check=True)

        #Checks codecs and converts if necessary
        check_codec = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=codec_type,codec_name',
            '-of', 'json',
            download_file_path
            ]
        codec_output = subprocess.check_output(check_codec, text=True)
        codec_data = json.loads(codec_output)

        video_codec = None
        audio_codec = None

        for stream in codec_data.get('streams', []):
            if stream['codec_type'] == 'video':
                video_codec = stream['codec_name']
            elif stream['codec_type'] == 'audio':
                audio_codec = stream['codec_name']

        accepted_codecs = ['h264', 'h265', 'aac', 'mp3']

        if video_codec not in accepted_codecs or audio_codec not in accepted_codecs:

            converted_file_path = download_file_path.replace(".mp4", "_converted.mp4")

            convert_command = [
                'ffmpeg',
                '-i', download_file_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                converted_file_path
                ]
        
            subprocess.run(convert_command)
            #os.remove(download_file_path)

        if converted_file_path:
            return True, converted_file_path
        else:
            return True, download_file_path

    except Exception as e:
        print(e)
        return False, None
    
def record_live_link(link, name):

    now = datetime.now()
    savetime = now.strftime("%Y_%m_%d_%H%M%S")

    link = link.strip()

    download_file_path = f'/mount/src/global-media/Recordings/{name}_{savetime}.mp4'

    if 'ffmpeg_link_record_process' not in st.session_state:
        st.session_state.ffmpeg_link_record_process = None

    def start_ffmpeg():

        record_live_link_command = [
            'ffmpeg',
            '-i', link,
            '-c', 'copy',
            download_file_path
            ]
        
        st.session_state.ffmpeg_link_record_process = subprocess.Popen(
            record_live_link_command,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True,
            buffsize=1
            )
        
        st.write("Recording...")

    def stop_ffmpeg():

        if st.session_state.ffmpeg_link_record_process:
            st.session_state.ffmpeg_link_record_process.stdin.write('q\n')
            st.session_state.ffmpeg_link_record_process.stdin.flush()
            st.session_state.ffmpeg_link_record_process.wait()

            st.write("Recording stopped.")
            st.session_state.ffmpeg_process = None