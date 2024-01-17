import streamlit as st
import os

path = "/mount/src/global-media/Recordings"
st.write(os.listdir(path))

with open("/mount/src/global-media/Recordings/files_list.txt", 'r') as f:
    doc = f.read()

st.write(doc)
st.write(len(doc))