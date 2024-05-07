import subprocess
import os
from datetime import datetime

segment_file_path = "/home/casey/Videos/CCTV_13/"
output_file_path = "/home/casey/Videos/Concat/"
concat_list = output_file_path + "concat_list.txt"

def find_indices():
    video_segments_list = os.listdir(segment_file_path)
    video_segments_list.sort()

    video_segments_dict = {}

    for index, item in enumerate(video_segments_list):
        video_segments_dict[index] = item

    return video_segments_dict

def add_to_concat_list(video_segment_dict, start_index, end_index):

    try:
        selected_segments = [segment_file_path + value for key, value in video_segment_dict.items() if start_index <= key <= end_index]

        with open(concat_list, 'w') as f:
            for item in selected_segments:
                f.write(f"file '{item}'\n")

        return True
    
    except Exception as e:
        print(e)

def concat(concat_list):

    try:
        start_time = datetime.now()
        start_time_str = start_time.strftime("%Y_%m_%d_%H_%M_%S")

        output_file = output_file_path + f"combined_video_{start_time_str}.mp4"

        concat_command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list,
            '-c', 'copy',
            output_file
            ]

        subprocess.run(concat_command, check=True)

        return output_file
    except Exception as e:
        print(f"Error occurred during concatation...\n{e}")

video_segments_dict = find_indices()

try:
    while True:
    
        user_input = input("Do you have the file names to concat? (y/n)\n")

        if user_input == "n":
            for key, value in video_segments_dict.items():
                print(str(key) + " -- " + value)

        if user_input == "y":
            start_index = int(input("Enter index for first file: "))
            end_index = int(input("Enter index for last file: "))

            if start_index in video_segments_dict.keys() and end_index in video_segments_dict.keys():

                create_concat_list = add_to_concat_list(video_segments_dict, start_index, end_index)
                if create_concat_list == True:
                    concat_process = concat(concat_list)
                    print(f"*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\nFile successfully created\n{concat_process}\n*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")

            else:
                print("Start or end index not found.")

except KeyboardInterrupt:
    print("\nProccess terminated.")