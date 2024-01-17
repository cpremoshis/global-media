import streamlit as st
import os

path = "/mount/src/global-media/Recordings"
st.write(os.listdir(path))