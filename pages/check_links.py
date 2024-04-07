import streamlit as st
import requests
import pandas as pd

with open("./Assets/broadcasters.csv") as file:
    df = pd.read_csv(file)

mpd_links = df[df['Format'] == "MPD"]['Playback M3U8']
m3u8_play_links = df[df['Format'] == "M3U8"]['Playback M3U8']
youtube_links = df[df['Format'] == "YouTube"]['Playback M3U8']

st.write(mpd_links)
st.write(m3u8_play_links)
st.write(youtube_links)