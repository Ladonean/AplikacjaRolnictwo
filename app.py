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



    




df = 'Stacje.csv'

st.dataframe(df)
    


