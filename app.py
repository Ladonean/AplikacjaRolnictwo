import streamlit as st
import pandas as pd

# Funkcja do załadowania obrazu tła
page_bg_img= """
        <style>
        </style>
        """


# Dodaj tło z lokalnego pliku
st.markdown(page_bg_img, unsafe_allow_html=True)

# Reszta kodu Streamlit
st.title("Moja aplikacja Streamlit z tłem")

