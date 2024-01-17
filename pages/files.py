import streamlit as st
import os

st.set_page_config(
    page_title="Files",
    layout="wide",
    initial_sidebar_state="expanded"
    )

current_path = os.path.dirname(os.path.abspath(__file__))
st.write(current_path)