import requests
import subprocess
import time
import openai
import ffmpeg
from io import BytesIO
import os
import threading

m3u8_url = "https://live-play.cctvnews.cctv.com/cctv/merge_cctv13.m3u8"
root_url = "https://live-play.cctvnews.cctv.com/cctv/"

ts_save_path = "/Users/casey/Downloads/live_translate/segments/"
ts_path_to_check = "/Users/casey/Downloads/live_translate/segments/merge_cctv13/"
raw_chunks_path = "/Users/casey/Downloads/live_translate/segments/raw_chunks/"
m3u8_video_path = "/Users/casey/Downloads/live_translate/M3U8/"
m3u8_playlist_path = "/Users/casey/Downloads/live_translate/M3U8/playlist.m3u8"
translation_path = "/Users/casey/Downloads/live_translate/segments/translation/"

translate = True

def delete_old_files(ts_path_to_check, raw_chunks_path, translation_path):
    
    try:
        for filename in os.listdir(ts_path_to_check):
            file_path = os.path.join(ts_path_to_check, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print("Failed to delete files.")

        for filename in os.listdir(raw_chunks_path):
            file_path = os.path.join(raw_chunks_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print("Failed to delete files.")

        for filename in os.listdir(translation_path):
            file_path = os.path.join(translation_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print("Failed to delete files.")
    except Exception as e:
        print(e)

def ffmpeg_concat(ts_files_to_concat, segment_tracker):
        
        segments_to_concat = ts_files_to_concat
        ts_files_to_concat = []

        #Starting string that will be added to and eventually fed to ffmpeg
        concat_string = "concat:"

        #The only difference between the "if" and "else" is that the "else" block does not add a "|" after the file name,
        #as the last file in the list must end with ."ts" not ".ts|"
        for number in range(0, len(segments_to_concat)):
            if number != len(segments_to_concat) - 1:
        
                item = segments_to_concat[number]

                try:
                    concat_string = concat_string + item + "|"
                except:
                    pass
            
            else:

                item = segments_to_concat[number]

                try:
                    concat_string = concat_string + item
                except:
                    pass

        output_file = raw_chunks_path + f"raw_{segment_tracker}.ts"

        print("Combining files.")

        #For MP4
        #command = [
        #    'ffmpeg',
        #    '-y',
        #    '-i', concat_string,
        #    '-c:v', 'libx264',
        #    '-c:a', 'aac',
        #    output_file
        #]

        #For TS
        command = [
            'ffmpeg',
            '-y',
            '-i', concat_string,
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_file
        ]

        subprocess.run(command)

        return output_file

def translate_audio(video_file, segment_tracker):
    try:
        openai.api_key = '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'
        translation_srt = f"/Users/casey/Downloads/live_translate/segments/translation/translation_{segment_tracker}.srt"
        mp3_for_openai = f"/Users/casey/Downloads/live_translate/segments/translation/translate_{segment_tracker}.mp3"

        input_file = ffmpeg.input(video_file)
        input_file.output(mp3_for_openai, acodec="mp3").run()

        # Read the audio file into a BytesIO object
        with open(mp3_for_openai, 'rb') as f:
            audio_bytes = BytesIO(f.read())
            audio_bytes.name = f"audio_{segment_tracker}.mp3"

        translation = openai.audio.translations.create(
            file = audio_bytes,
            model='whisper-1',
            response_format="srt"
        )

        with open(translation_srt, 'w') as file:
            file.write(translation)

        return translation_srt
    except Exception as e:
        return e

def wrap_final_video(output_file, translation_srt='translation_srt'):

    try:
            if translate == True:
                final_video = m3u8_video_path + f"final_video_{segment_tracker}.ts"

                subtitle_style = "force_style='Alignment=2,Fontsize=24,PrimaryColour=&H00ffffff,BackColour=&H80000000,BorderStyle=3,OutlineColour=&H00000000,Shadow=0'"
                video_resolution = "854x480"

                #For MP4 files
                #command = [
                #    'ffmpeg',
                #    '-y',
                #    '-i', output_file,
                #    '-i', translation_srt,
                #    '-c', 'copy',
                #    '-c:s', 'mov_text',
                #    final_video
                #]

                #For TS files
                command = [
                    'ffmpeg',
                    '-y',
                    '-i', output_file,
                    '-vf', f'scale={video_resolution},subtitles={translation_srt}:{subtitle_style}',
                    '-c:v', 'libx264',
                    '-c:a', 'copy',
                    final_video
                ]

                subprocess.run(command)

                return final_video
            
            else:
                final_video = m3u8_video_path + f"final_video_{segment_tracker}.ts"

                #For MP4 files
                #command = [
                #    'ffmpeg',
                #    '-y',
                #    '-i', output_file,
                #    '-i', translation_srt,
                #    '-c', 'copy',
                #    '-c:s', 'mov_text',
                #    final_video
                #]

                #For TS files
                command = [
                    'ffmpeg',
                    '-y',
                    '-i', output_file,
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    final_video
                ]

                subprocess.run(command)

                return final_video

    except Exception as e:
        return e

def get_video_duration(final_video):

    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        final_video
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        duration = result.stdout.decode('utf-8').strip()

        return str(duration)
    
    except Exception as e:
        print(e)

def update_m3u8(final_video):
    
    duration = get_video_duration(final_video)

    updates = [f'#EXTINF:{duration},\n', final_video.split("/")[6] + "\n"]

    with open(m3u8_playlist_path, 'a') as f:
        f.writelines(updates)

delete_old_files(ts_path_to_check, raw_chunks_path, translation_path)

#----> THREADING <----
def download_ts_segments(ts_save_path):

    print("Collecting .ts files from source.")

    ts_files_downloaded = []

    while True:

        response = requests.get(m3u8_url)

        if response.status_code == 200:
            
            lines = response.text.splitlines()

            for line in lines:
                if ".ts" in line:
                    if root_url + line not in ts_files_downloaded:

                        response = requests.get(root_url + line)
                        with open(ts_save_path + line, 'wb') as f:
                            f.write(response.content)

                        ts_files_downloaded.append(root_url + line)

        else:
            pass

        time.sleep(4)

thread1 = threading.Thread(target=download_ts_segments, args=(ts_save_path,))

thread1.start()
#----> END OF THREADING <----


#----> RESETS M3U8 PLAYLIST <----
m3u8_template = ['#EXTM3U\n', '#EXT-X-VERSION:3\n', '#EXT-X-TARGETDURATION:30\n', '#EXT-X-MEDIA-SEQUENCE:0\n\n']

with open(m3u8_playlist_path, 'w') as f:
    f.writelines(m3u8_template)
#----> END OF RESETTING M3U8 PLAYLIST <----

ts_files_on_disk = []
ts_files_to_concat = []
ts_files_used = []
segment_tracker = 0

while True:

    ts_files_to_check = sorted(
        [os.path.join(ts_path_to_check, file) for file in os.listdir(ts_path_to_check) if ".ts" in file],
        key=lambda x:x.lower()                 
        )

    for file in ts_files_to_check:

        #Checks if this file was just downloaded
        if file not in ts_files_on_disk:
            
            ts_files_on_disk.append(file)
            
            if file not in ts_files_used:

                ts_files_to_concat.append(file)

                print(len(ts_files_to_concat))

        if len(ts_files_to_concat) >= 8:
            
            segment_tracker += 1

            output_file = ffmpeg_concat(ts_files_to_concat, segment_tracker)

            if translate == True:
                translation_srt = translate_audio(output_file, segment_tracker)
                final_video = wrap_final_video(output_file, translation_srt)
            
                update_m3u8(final_video)

            elif translate == False:
                final_video = wrap_final_video(output_file)
                update_m3u8(final_video)

            #Lists the ts files as used, clears the list of ts files to concat
            for file in ts_files_to_concat:
                ts_files_used.append(file)
            
            ts_files_to_concat = []

            print(final_video)
            
            #break
        else:
            pass

    time.sleep(3)