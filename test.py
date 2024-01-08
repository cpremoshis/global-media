import streamlit as st
import requests
import time

m3u8_url = "https://live-hls-web-aje-fa.getaj.net/AJE/02.m3u8"
root_url = "https://live-hls-web-aje-fa.getaj.net/AJE/"

#Enter seconds in intervals of FIVE
def fetch_urls(seconds):
    text = requests.get(m3u8_url)

    lines = text.text.splitlines()

    ts_files = [line for line in lines if line.endswith(".ts")]

    for item in ts_files:
        if root_url + item not in files_list:
            files_list.append(root_url + item)

    #This is the .ts file that most closely corresponds to the time when user began recording
    record_start = files_list[-1]

    cycles = seconds / 5

    for cycle in cycles:

        text = requests.get(m3u8_url)

        lines = text.text.splitlines()

        ts_files = [line for line in lines if line.endswith(".ts")]

        for item in ts_files:
            if root_url + item not in files_list:
                files_list.append(root_url + item)

        cycles = cycle - 1

        if cycles != 0:
            time.sleep(5)
        else:
            pass

    return record_start

files_list = []

record_start = fetch_urls(30)

#container = st.empty()

#while True:

#    fetch_urls()

#    container.empty()
#    container.write(files_list)

#    time.sleep(5)