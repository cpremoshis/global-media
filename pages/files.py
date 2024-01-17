import streamlit as st
import os

st.set_page_config(
    page_title="Files",
    layout="wide",
    initial_sidebar_state="expanded"
    )

recordings_path = "/mount/src/global-media/Recordings"
st.write(os.listdir(recordings_path))