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
    




df = 'Stacje.csv'

st.dataframe(df)
    
with st.container():
        address = st.text_input("Wpisz adres:", "Czaple, Kartuzy")
        coords = geocode_address(address)
        if coords:
            m = folium.Map(location = [53,18], zoom_start = 10, tiles="Esri.WorldImagery")
            folium.Marker(
                location=[53,18]
            ).add_to(m)

            
            marker_cluster = MarkerCluster().add_to(m)
            for idx, row in df.iterrows():
                folium.Marker(location=[row['Y'], row['X']], popup=row['Stacja']).add_to(marker_cluster)
            
            folium.LayerControl().add_to(m)
            
            st_folium (m, width=1600)


