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
        /*Sidebar : Navigation list*/
        div.element-container:nth-child(4) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(1) {
        margin: 0;
        padding: 0;
        list-style: none;
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
        st.title(App")
        st.subheader("Menu:")
        st.markdown(
            """
                - [Data](#data)
                - [Mapa](#mapa)
                - [Opady](#Opady)
                - [About](#about)
            """)

# Run the app
if __name__ == "__main__":
    main()
