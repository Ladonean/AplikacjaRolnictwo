import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="App",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
    'About': "https://github.com/Ladonean/Nauka/tree/main"
    }
)

# Funkcja do załadowania obrazu tła
page_bg_img= """
        <style>
        /* Smooth scrolling*/
        .main {
        scroll-behavior: smooth;
        }
        /* main app body with less padding*/
        .st-emotion-cache-z5fcl4 {
        padding-block: 0;
        }


        .stApp {
        background-color: #e6ffe6;
        }
        </style>
        """

# Dodaj tło z lokalnego pliku
st.markdown(page_bg_img, unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.title("App")
        st.subheader("Menu:")
        st.markdown(
            """
                - [Data](#data)
                - [Mapa](#mapa)
                - [Opady](#Opady)
                - [About](#about)
            """)
        
    with st.container():
        st.title("App opady")
        st.markdown("Aplikacja sluzaca do sprawdzania opadow i wskaznika ndvi na obszarze Polski")

# Run the app
if __name__ == "__main__":
    main()
