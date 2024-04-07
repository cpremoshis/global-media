import streamlit as st
import requests
import pandas as pd

def check_links(row):
    if row['Format'] == "M3U8":
        link = row['Playback M3U8']
        response = requests.get(link)
        status = response.status_code

        return status
    
with open("./Assets/broadcasters.csv") as file:
    df = pd.read_csv(file)

df['Status'] = df.apply(check_links)

st.write(df['Name', 'Status'])