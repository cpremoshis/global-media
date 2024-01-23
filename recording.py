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
            #This block is for RTVE
            else:
                for item in ts_files:
                    if item not in files_list:
                        files_list.append(item)

            #This is the .ts file that SHOULD most closely corresponds to the time when user began recording
            record_start = files_list[-2]

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
                #This block is for RTVE
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

        #Combines .aac files using 'ffmpeg'
        elif media_type == "aac":
            command = [
                'ffmpeg',
                '-i', concat_string,
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

            return True, output_file, translation_file, audio_file
        
        else:
            return True, output_file

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

def combine_videos_ffmpeg(video_dict, output_path):
    
    try:
        command = ['ffmpeg']

        video_indices = []
        subtitle_indices = []
        index_counter = 0

        # Iterate over each item in the dictionary
        for outlet, paths in video_dict.items():
            command.extend(['-i', paths['Video']])
            video_indices.append(str(index_counter))
            index_counter += 1

            if 'Subtitles' in paths and paths['Subtitles'] != "None":                
                command.extend(['-i', paths['Subtitles']])
                subtitle_indices.append(str(index_counter))
                index_counter += 1

        # Number of videos
        num_videos = len(video_indices)

        #Framerate
        target_fps = 30

        # Constructing filter_complex
        filter_complex = ''
        if num_videos == 1:
            filter_complex += f'[0:v]fps=fps={target_fps},scale=1920:1080[v];'
        elif num_videos == 2:
            for i, idx in enumerate(video_indices):
                # Scale to fit within 960x1080, maintaining aspect ratio
                filter_complex += f'[{idx}:v]fps=fps={target_fps},scale=960:ih:force_original_aspect_ratio=decrease[padded{i}]; '
                # Pad to 960x1080 if necessary
                filter_complex += f'[padded{i}]pad=960:1080:(ow-iw)/2:(oh-ih)/2:black[v{i}]; '
            filter_complex += '[v0][v1]hstack=inputs=2[v];'
        elif num_videos == 3:
            for i in range(2):
                idx = video_indices[i]
                filter_complex += f'[{idx}:v]scale=960:540[v{i}]; '
            filter_complex += '[v0][v1]hstack=inputs=2[top]; '
            idx = video_indices[2]
            # Scale third video and pad to center it
            filter_complex += f'[{idx}:v]scale=-1:540, pad=1920:ih:(ow-iw)/2:(oh-ih)/2:black[bottom]; '
            filter_complex += '[top][bottom]vstack[v];'
        elif num_videos == 4:
            for i, idx in enumerate(video_indices):
                filter_complex += f'[{idx}:v]scale=960:540[v{i}]; '
            filter_complex += '[v0][v1]hstack=inputs=2[top]; '
            filter_complex += '[v2][v3]hstack=inputs=2[bottom]; '
            filter_complex += '[top][bottom]vstack[v];'

        command.extend(['-filter_complex', filter_complex])

        # Mapping video and audio streams
        command.extend(['-map', '[v]'])
        for idx in video_indices:
            command.extend(['-map', f'{idx}:a'])

        # Mapping subtitle streams and adding metadata
        for i, idx in enumerate(subtitle_indices):
            command.extend(['-map', idx])
            command.extend(['-metadata:s:s:' + str(i), f'title={list(video_dict.keys())[i]}'])

        command.extend(['-c:v', 'libx264', '-c:a', 'aac', '-c:s', 'mov_text', output_path])

        return command

        #subprocess.run(" ".join(command), shell=True)

        #return True
    
    except Exception as e:
        return e

def multi_record(*outlets, seconds, translate=False):

    try:

        now = datetime.now()
        savetime = now.strftime("%Y_%m_%d_%H%M%S")

        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            # Dictionary to hold future to outlet mapping
            future_to_outlet = {
                executor.submit(record_m3u8, outlet.name, seconds, outlet.recording_url, outlet.root_url, translate): outlet
                for outlet in outlets
            }

            results = []
            for future in as_completed(future_to_outlet):
                try:
                    # Get the result from the future
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"{future_to_outlet[future].name} generated an exception: {exc}")
            
        #return results
        
        video_dict = {}

        if len(results[0]) == 3:

            for item in results:
                if item[0] == True:
                    video_dict[item[1]] = {"Video":item[2], "Subtitles":"None"}

        combined_video = f"./Recordings/Combined_video_{savetime}.mp4"

        ffmpeg_status = combine_videos_ffmpeg(video_dict, combined_video)

        return video_dict, ffmpeg_status

    except Exception as e:
        return e


#create_ffmpeg_command_gpt(video_dict, output_path)

#video_dict = {name1:{'Video':video1, 'Subtitles':sub1}}
    
#recording, translation, audio



#Original ffmpeg command
#    command = [
#    'ffmpeg',
#    '-i', concat_string,
#    '-c', 'copy',
#    '-bsf:a', 'aac_adtstoasc',
#    output_file
#]