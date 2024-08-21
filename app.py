import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(
    page_title="Aplikacja Opady",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "https://github.com/Ladonean/Nauka/tree/main"
    }
)

# Funkcja do załadowania stylu tła
page_bg_img = """
        <style>
        /* Płynne przewijanie */
        .main {
        scroll-behavior: smooth;
        }
        /* główna część aplikacji z mniejszym paddingiem */
        .st-emotion-cache-z5fcl4 {
        padding-block: 0;
        }
        .stApp {
        background-color: #ffffff;
        }

        /* Usunięcie przerwy między sekcjami */
        .css-1lcbmhc, .css-18e3th9 {
            padding: 0;
        }
        </style>
        """

# Dodanie stylu tła
st.markdown(page_bg_img, unsafe_allow_html=True)

# Główna funkcja uruchamiająca aplikację
def main():
    with st.sidebar:
        st.title("Aplikacja Opady")
        st.subheader("Menu:")
        st.markdown(
            """
                - [Mapa](#mapa)
                - [Opady](#opady)
                - [Polska](#polska)
                - [About](#about)
            """)

    with st.container():
        st.title("Aplikacja Opady")
        st.markdown("Aplikacja służąca do sprawdzania opadów i wskaźnika NDVI na obszarze Polski")

# Uruchomienie aplikacji
if __name__ == "__main__":
    main()
