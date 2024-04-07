import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

def check_playback_links(row):
    if row['Format'] == "YouTube":
        link = row['Playback M3U8']
        response = requests.get(link)
        status = response.status_code

        return status
    
    if row['Format'] == "MPD":
        link = row['Playback M3U8']
        response = requests.get(link)
        status = response.status_code

        return status

    if row['Format'] == "M3U8":
        link = row['Playback M3U8']
        response = requests.get(link)
        status = response.status_code

        return status
    
def check_record_links(row):
    if row['Format'] == "YouTube":
        link = row['Playback M3U8']
        response = requests.get(link)
        if response.status_code == 200:
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            live_tag = soup.find('meta', attrs={'itemprop':'isLiveBroadcast'})

            if live_tag:
                is_live = live_tag['content']
                if is_live == "True":
                    end_tag = soup.find('meta', attrs={'itemprop':'endDate'})
                    if end_tag is None:
                        status = False
                        return status
                    else:
                        status = True
                        return status
    
with open("./Assets/broadcasters.csv") as file:
    df = pd.read_csv(file)

if st.button("Check links"):

    #df['Playback Status'] = df.apply(check_playback_links, axis=1)
    df['Record Status'] = df.apply(check_record_links, axis=1)

    st.write(df[['Name', 'Format', 'Record Status']])