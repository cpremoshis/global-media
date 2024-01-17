import streamlit as st
import os

st.set_page_config(
    page_title="Files",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
    )

path = "/mount/src/global-media/Recordings"
st.write(os.listdir(path))