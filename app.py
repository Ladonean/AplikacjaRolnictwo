import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Photon
import requests
from io import StringIO

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

def date_input_proc(input_date, time_range):
    end_date = input_date
    start_date = input_date - timedelta(days=time_range)
    
    str_start_date = start_date.strftime('%Y-%m-%d')
    str_end_date = end_date.strftime('%Y-%m-%d')
    return str_start_date, str_end_date
    
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
        
def wczytaj_stacje(url):
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Nie udało się pobrać danych stacji z podanego URL: " + url)
        return None
    data = response.content.decode('windows-1250')
    df = pd.read_csv(StringIO(data), delimiter=',', header=None)
    
    df.columns = ['X', 'Y', 'Stacja']
    df['X'] = df['X'].astype(float)
    df['Y'] = df['Y'].astype(float)
    
    return df
    

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

        
    with st.container():

                # Creating a 2 days delay for the date_input placeholder to be sure there are satellite images in the dataset on app start
                today = datetime.today()
                delay = today - timedelta(days=5)

                # Date input widgets
                st.success("Data P 📅")
                initial_date = st.date_input("initial", value=delay, label_visibility="collapsed")
    
    with st.container():
        address = st.text_input("Wpisz adres:", "Czaple, Kartuzy")
        coords = geocode_address(address)
        if coords:
            m = folium.Map(location = coords, zoom_start = 10, tiles="Esri.WorldImagery")
            folium.Marker(
                location=coords,
                popup=address,
            ).add_to(m)
            path_stacje = "https://github.com/Ladonean/Nauka/blob/main/Stacje.csv"
            
            df_baza = wczytaj_stacje(path_stacje)
            
            marker_cluster = MarkerCluster().add_to(m)
            for idx, row in df.iterrows():
                folium.Marker(location=[row['Y'], row['X']], popup=row['Stacja']).add_to(marker_cluster)
            folium.LayerControl().add_to(m)
            
            st_folium (m, width=1600)
        else:
            st.write("Wrong")


# Run the app
if __name__ == "__main__":
    main()

