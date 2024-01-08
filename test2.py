import requests
import time
import subprocess
from tqdm import tqdm
    
#    m3u8_url = "https://live-hls-web-aje-fa.getaj.net/AJE/02.m3u8"
#    root_url = "https://live-hls-web-aje-fa.getaj.net/AJE/"
#    output_file = "/Users/casey/Downloads/CONCAT TEST.mp4"
#    output_file = "./Recording/CONCAT TEST.mp4"

#Enter seconds in intervals of FIVE
def record_m3u8(seconds, playlist_url, root_url, output_file):

    try:
        files_list = []

        text = requests.get(playlist_url)
        lines = text.text.splitlines()

        #List of .ts files in M3U8 file
        ts_files = [line for line in lines if line.endswith(".ts")]

        #Adds any .ts file to "files_list" if that .ts file is not already present
        for item in ts_files:
            if root_url + item not in files_list:
                files_list.append(root_url + item)

        #This is the .ts file that most closely corresponds to the time when user began recording
        record_start = files_list[-1]

        cycles = seconds / 5

        #Reloads M3U8 playlist every 5 seconds, adding new .ts files to 'files_list'
        for number in tqdm(range(int(cycles)), desc="Logging .ts files"):

            text = requests.get(playlist_url)

            lines = text.text.splitlines()

            ts_files = [line for line in lines if line.endswith(".ts")]

            for item in ts_files:
                if root_url + item not in files_list:
                    files_list.append(root_url + item)

            time.sleep(5)

        #Creates a new list only with the "record_start" .ts file and those AFTER it
        record_start_index = files_list.index(record_start)
        files_list_final = files_list[record_start_index:]

        #Starting string that will be added to and eventually fed to ffmpeg
        concat_string = "concat:"

        #The only difference between the "if" and "else" is that the "else" block does not add a "|" after the file name,
        #as the last file in the list must end with ."ts" not ".ts|"
        for number in tqdm(range(0, len(files_list_final)), "Saving .ts files"):
            if number != len(files_list_final) - 1:
        
                item = files_list_final[number]

#                file_path = f"/Users/casey/Downloads/ts_file_{number}.ts"
                file_path = f"./Recording/ts_file_{number}.ts"

                response = requests.get(item)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    concat_string = concat_string + file_path + "|"
                else:
                    pass
            
            else:
                item = files_list_final[number]

#                file_path = f"/Users/casey/Downloads/ts_file_{number}.ts"
                file_path = f"./Recording/ts_file_{number}.ts"

                response = requests.get(item)
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)

                    concat_string = concat_string + file_path
                else:
                    pass

        #Combines .ts files using 'ffmpeg'
        command = [
            'ffmpeg',
            '-i', concat_string,
            '-c', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            output_file
        ]

        subprocess.run(command)

        return "Success."

    except Exception as error:

        return error

#    record = record_m3u8(30, m3u8_url, root_url, output_file)

#    print(record)


#container = st.empty()

#while True:

#    fetch_urls()

#    container.empty()
#    container.write(files_list)

#    time.sleep(5)