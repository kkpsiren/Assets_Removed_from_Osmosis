import pandas as pd
import requests
import base64
import streamlit as st


@st.cache()
def read_flipside(url):
    r = requests.get(url)
    r = r.json()
    df = pd.DataFrame(r).sort_values("BLOCK_TIMESTAMP", ascending=False)
    df["BLOCK_TIMESTAMP"] = pd.to_datetime(df["BLOCK_TIMESTAMP"])
    return df


