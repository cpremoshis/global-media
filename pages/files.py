import streamlit as st
import os

path = "/mount/src/global-media/Recordings"
files = os.listdir(path)

st.write(files)

