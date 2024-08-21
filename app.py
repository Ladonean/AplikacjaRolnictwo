import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Główna funkcja uruchamiająca aplikację
def main():

    with st.container():
        st.title("Aplikacja Opady")
        st.markdown("Aplikacja służąca do sprawdzania opadów i wskaźnika NDVI na obszarze Polski")

# Uruchomienie aplikacji
if __name__ == "__main__":
    main()
