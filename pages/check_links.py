import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import subprocess

def check_playback_links(row):
    try:
        if row['Format'] == "YouTube":
            link = row['Playback M3U8']
            response = requests.get(link, timeout=5)
            status = response.status_code

            return status
        
        if row['Format'] == "MPD":
            link = row['Playback M3U8']
            response = requests.get(link, timeout=5)
            status = response.status_code

            return status

        if row['Format'] == "M3U8":
            link = row['Playback M3U8']
            response = requests.get(link, timeout=5)
            status = response.status_code

            return status
    except:
        pass
    
def check_record_links(row):
    try:
        if row['Format'] == "YouTube":
            link = row['Playback M3U8']
            response = requests.get(link, timeout=5)
            if response.status_code == 200:
                html = response.content
                soup = BeautifulSoup(html, 'html.parser')
                live_tag = soup.find('meta', attrs={'itemprop':'isLiveBroadcast'})

                if live_tag:
                    is_live = live_tag['content']
                    if is_live == "True":
                        end_tag = soup.find('meta', attrs={'itemprop':'endDate'})
                        if end_tag is None:
                            status = True
                            return status
                        else:
                            status = False
                            return status
                        
        if row['Format'] == "MPD":
            status = True
            return True
        
        if row['Format'] == "M3U8":
            record_link = row['Recording M3U8']
            root_link = row['Root URL']

            manifest_response = requests.get(record_link, timeout=5)
            if manifest_response.status_code == 200:

                lines = manifest_response.text.splitlines()
                ts_files = [line for line in lines if ".ts" in line or ".aac" in line]

                if root_link != "Null":
                    test_file = root_link + ts_files[0]
                    test_file_response = requests.get(test_file, timeout=5)
                    if test_file_response.status_code == 200:
                        status = True
                        return status
                    else:
                        status = False
                        return status
                #This block is for RTVE, BBC TV
                else:
                    test_file = ts_files[0]
                    test_file_response = requests.get(test_file, timeout=5)
                    if test_file_response.status_code == 200:
                        status = True
                        return status
                    else:
                        status = False
                        return status
    except:
        pass

with open("./Assets/broadcasters.csv") as file:
    df = pd.read_csv(file)

if st.button("Check links"):

    status = st.empty()

    status.status("Checking PLAYBACK statuses")
    df['Playback Status'] = df.apply(check_playback_links, axis=1)
    status.status("Checking RECORD statuses")
    df['Record Status'] = df.apply(check_record_links, axis=1)

    st.write(df[['Name', 'Format', 'Playback Status', 'Record Status']])