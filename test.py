import streamlit as st
import requests
import ffmpeg
import time

url = "https://live-hls-web-aje-fa.getaj.net/AJE/03.m3u8"
root_url = "https://live-hls-web-aje-fa.getaj.net/AJE/"

def fetch_urls():
    text = requests.get(url)

    lines = text.text.splitlines()

    ts_files = [line for line in lines if line.endswith(".ts")]

    for item in ts_files:
        if root_url + item not in files_list:
            files_list.append(root_url + item)

files_list = []

container = st.empty()

while True:

    fetch_urls()

    container.empty()
    container.write(files_list)

    time.sleep(5)