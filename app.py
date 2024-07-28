import streamlit as st
import pandas as pd

# Funkcja do załadowania obrazu tła
page_bg_img= """
        <style>
        [data-testid="stAppViewContainer"]{
            background-image: url("https://github.com/Ladonean/Nauka/blob/main/nature-fcp.png");
            background-size: cover;
        }

        [data-testid=""stHeader"]{
            background-color: rgba(0, 0, 0, 0);
        }

        [data-testid="stToolbar"] {
        }
        </style>
        """


# Dodaj tło z lokalnego pliku
st.markdown(page_bg_img, unsafe_allow_html=True)

# Reszta kodu Streamlit
st.title("Moja aplikacja Streamlit z tłem")
st.write("Przykładowa zawartość aplikacji")


st.write('Hello, *World!* :sunglasses:')

df = pd.DataFrame({
     'first column': [1, 2, 3, 4],
     'second column': [10, 20, 30, 40]
     })
st.write(df)
