import streamlit as st
import requests
import pandas as pd

with open("./Assets/broadcasters.csv") as file:
    df = pd.read_csv(file)

st.write(df)