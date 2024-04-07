import streamlit as st
import requests
import pandas as pd

with open("./Assets/broadcasters.csv") as file:
    df = pd.read_csv(file)

mpd_links = df[df['Format'] == "MPD"]['Playback M3U8']
st.write(mpd_links)