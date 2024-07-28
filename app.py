import streamlit as st
import pandas as pd

# Funkcja do załadowania obrazu tła
page_bg_img= """
        <style>
        .stApp {
                background-color: #e6ffe6;
                }
        </style>
        """


# Dodaj tło z lokalnego pliku
st.markdown(page_bg_img, unsafe_allow_html=True)

st.sidebar.button()

# Reszta kodu Streamlit
st.title("App")

