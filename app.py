import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime, timedelta
from geopy.geocoders import Photon
from geopy.exc import GeocoderTimedOut

st.set_page_config(
    page_title="Aplikacja",
    layout="wide",
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
        background-color: #e6ffe6;
        }
        .map-container {
            width: 800px; /* Ustaw szerokość kontenera mapy */
            height: 800px; /* Ustaw wysokość kontenera mapy */

        }
        /* Usunięcie przerwy między sekcjami */
        .css-1lcbmhc {
            padding: 0;
        }
        </style>
        """

# Dodanie stylu tła
st.markdown(page_bg_img, unsafe_allow_html=True)

# Funkcja do przetwarzania daty
def date_input_proc(input_date, time_range):
    end_date = input_date
    start_date = input_date - timedelta(days=time_range)
    str_start_date = start_date.strftime('%Y-%m-%d')
    str_end_date = end_date.strftime('%Y-%m-%d')
    return str_start_date, str_end_date

# Funkcja do geokodowania adresu
def geocode_address(address):
    geolocator = Photon(user_agent="measurements")
    try:
        location = geolocator.geocode(address)
        if location:
            return [location.latitude, location.longitude]
        else:
            return None
    except GeocoderTimedOut:
        return None

# Funkcja do ładowania danych
def load_data(url):
    df = pd.read_csv(url, encoding='windows-1250', header=None)
    df.columns = ['X', 'Y', 'Stacja']
    return df

# Główna funkcja uruchamiająca aplikację
def main():
    with st.sidebar:
        st.title("Aplikacja")
        st.subheader("Menu:")
        st.markdown(
            """
                - [Data](#data)
                - [Mapa](#mapa)
                - [Opady](#opady)
                - [About](#about)
            """)

    with st.container():
        st.title("Aplikacja Opady")
        st.markdown("Aplikacja służąca do sprawdzania opadów i wskaźnika NDVI na obszarze Polski")

    with st.container():
        today = datetime.today()
        delay = today - timedelta(days=5)
        st.success("Data 📅")
        initial_date = st.date_input("Data początkowa", value=delay, label_visibility="collapsed")

    with st.container():
        address = st.text_input("Wpisz adres:", "Czaple, Kartuzy")
        coords = geocode_address(address)
        if coords:
            m = folium.Map(location=coords, zoom_start=10, tiles="Esri.WorldImagery")
            folium.Marker(
                location=coords,
                popup=address,
            ).add_to(m)
            st_folium(m, width=800, height=800)  # Dostosowanie szerokości i wysokości mapy
        else:
            st.write("Nie udało się zlokalizować adresu.")

    with st.container():
        csv_url = "https://raw.githubusercontent.com/Ladonean/Nauka/main/Stacje.csv?raw=true"
        data = load_data(csv_url)
        st.dataframe(data)

# Uruchomienie aplikacji
if __name__ == "__main__":
    main()
