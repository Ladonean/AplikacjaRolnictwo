import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from geopy.geocoders import Photon
from geopy.exc import GeocoderTimedOut
import geemap.foliumap as geemap
import ee
import numpy as np
from PIL import Image
from datetime import datetime, timezone, timedelta
import requests
from io import StringIO
import geopandas as gpd
from geokrige.tools import TransformerGDF
import calendar
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
import json
from google.oauth2 import service_account

st.set_page_config(
    page_title="Aplikacja Opady",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "https://github.com/Ladonean/Nauka/tree/main"
    }
)

json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]

json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)
# Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)

st.write("Google Earth Engine is authenticated and initialized!")
        
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

# Funkcja do geokodowania adresu
def geocode_address(address):
    geolocator = Photon(user_agent="app",timeout=10)
    try:
        location = geolocator.geocode(address)
        if location:
            return [location.latitude, location.longitude]
        else:
            return None
    except GeocoderTimedOut:
        return None

# Funkcja NDVI
#ee.Authenticate() 
#ee.Initialize(project='ee-ladone')



# Wczytanie csv ze opadami
def wczytaj_csv(url):
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Nie udało się pobrać danych z podanego URL: " + url)
        return None
    data = response.content.decode('windows-1250')
    df = pd.read_csv(StringIO(data), delimiter=',', header=None)
    df = df.iloc[:, [1, 2, 3, 4, 5]]
    df.columns = ['Stacja', 'Rok', 'Miesiąc', 'Dzień', 'Opady']
    
    return df

# Wczytanie csv ze stacjami
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

# Funkcja łącząca lokalizacje stacji z danymi o opadach
def merge_data(location_data, rain_data, selected_date):
    rain_data_filtered = rain_data[
        (rain_data['Rok'] == selected_date.year) &
        (rain_data['Miesiąc'] == selected_date.month) &
        (rain_data['Dzień'] == selected_date.day)
    ]
    location_data['Stacja'] = location_data['Stacja'].str.strip()
    rain_data_filtered.loc[:, 'Stacja'] = rain_data_filtered['Stacja'].str.strip()
    merged_data = location_data.merge(rain_data_filtered, on='Stacja', how='inner')
    return merged_data

def plot_wynik(path_shp, Wynik, title):
    X = np.column_stack([Wynik['X'], Wynik['Y']])
    y = np.array(Wynik['Opady'])

    granica = gpd.read_file(path_shp).to_crs(crs='EPSG:4326')
    transformer = TransformerGDF()
    transformer.load(granica)
    meshgrid = transformer.meshgrid(density=3)
    mask = transformer.mask()

    X_siatka, Y_siatka = meshgrid

    # Aproksymacja wielomianowa z wygładzaniem 1
    rbf_interpolator = Rbf(X[:, 1], X[:, 0], y, function='multiquadric', smooth=1)
    Z_siatka = rbf_interpolator(X_siatka, Y_siatka)
    Z_siatka[~mask] = None

    fig, ax = plt.subplots()
    granica.plot(facecolor='none', edgecolor='black', linewidth=1.5, zorder=5, ax=ax)
    y_s = np.sort(y)[-5:]
    avg5 = np.mean(y_s)
    cbar = ax.contourf(X_siatka, Y_siatka, Z_siatka, cmap='YlGnBu', levels=np.arange(0, avg5, 2), extend='min')
    cax = fig.add_axes([0.93, 0.134, 0.02, 0.72])
    colorbar = plt.colorbar(cbar, cax=cax, orientation='vertical')

    ax.grid(lw=0.3)
    ax.set_title(title, fontweight='bold', pad=15)

    return fig, ax


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

    with st.container():
        end_date = st.date_input("Wybierz datę końcową", value=datetime.today())

        start_date = end_date - timedelta(weeks=2)

        # st.success(f"Dzisiejsza data: {datetime.today()}")
        # st.write(f"Wybrana data początkowa: {start_date.strftime('%Y-%m-%d')}")
        # st.write(f"Wybrana data końcowa: {end_date.strftime('%Y-%m-%d')}")


    with st.container():
        st.markdown('<h2 id="mapa">Mapa</h2>', unsafe_allow_html=True)
        address = st.text_input("Wpisz adres:", "Czaple, Kartuzy")
        coords = geocode_address(address)


        if coords:

            def get_image(start_date, end_date, coords):
                # Pobieranie kolekcji obrazów Landsat 8 (Collection 2 Level 2)
                point = ee.Geometry.Point([coords[1], coords[0]])
                buffer = point.buffer(10000)
                collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                    .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                    .filterBounds(buffer)
                
                # Zamiast median(), wybierz pierwszy obraz w kolekcji
                image = collection.first()
                
                # Pobranie daty obrazu
                image_date = image.get('system:time_start').getInfo()
                
                if image_date is not None:
                    image_date = datetime.fromtimestamp(image_date / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
                else:
                    image_date = "Brak dostępnej daty"
                
                return image, image_date, buffer


        # Ustawienia początkowe dat
            if st.button("Generuj Mapę"):
                image, image_date, buffer = get_image(start_date, end_date,coords)
    
    
                # Obliczanie NDVI dla wybranego obrazu
                ndvi_image = image.normalizedDifference(['B5', 'B4']).rename('NDVI').clip(buffer)
                # Obliczanie NDVI dla wybranego obrazu
                ndwi_image = image.normalizedDifference(['B3', 'B5']).rename('NDVI').clip(buffer)
                
                ndvi_map_id_dict = geemap.ee_tile_layer(
                    ndvi_image,
                    vis_params={
                    'min': -0.3, 
                    'max': 0.8,
                    'palette': ['#a50026', '#d73027', '#fdae61', '#1a9850', '#006837']
                    },
                    name="NDVI"
                    )
                
                
                ndwi_map_id_dict = geemap.ee_tile_layer(
                    ndwi_image,
                    vis_params={
                    'min': -0.6, 
                    'max': 0.3, 
                    'palette': ['#a50026', '#ffffbf', '#87a6ff']
                    },
                    name="NDWI"
                    )
                
                m = folium.Map(location=coords, zoom_start=10, tiles="Esri.WorldImagery")
                folium.Marker(
                    location=coords,
                    popup=address,
                ).add_to(m)
    
                m.add_child(ndvi_map_id_dict)
                m.add_child(ndwi_map_id_dict)
    
    
                folium.LayerControl().add_to(m)
    
                st_folium(m, width=600, height=600)  # Dostosowanie szerokości i wysokości mapy
            
            else:
                st.write("Nie udało się zlokalizować adresu.")
    
    with st.container():
        st.success(f"Data zdjęcia satelity {image_date}")

    with st.container():
        st.subheader("NDVI - Normalized Difference Vegetation Index")
        st.write("""
                Wskaźnik NDVI jest narzędziem niezwykle ważnym dla rolników, pozwalającym na monitorowanie plonów oraz wykrywanie problemów związanych z niedoborem wody czy chorobami roślin. 
                Dzięki danym pochodzącym z satelitarnej obserwacji Ziemi, rolnicy mogą uzyskać szybki i dokładny obraz stanu roślinności na swoich uprawach.
                """)
        
        st.subheader("NDWI - Normalized Difference Water Index")
        st.write("""
                Wskaźnik NDWI służy do monitorowania zmian związanych z zawartością wody w zbiornikach wodnych. 
                Ponieważ zbiorniki wodne silnie absorbują światło w widzialnym i podczerwonym spektrum elektromagnetycznym, NDWI wykorzystuje pasma zielone i bliskiej podczerwieni, aby wyodrębnić zbiorniki wodne. 
                Wskaźnik ten jest czuły na tereny zurbanizowane, co może prowadzić do przeszacowania obszarów wodnych.
                """)
    
    # if st.button("Generuj Mapę"):
    #     folium.LayerControl().add_to(m)

    #     m.save("example_123.html")

    with st.container():
        st.markdown('<h2 id="opady">Opady</h2>', unsafe_allow_html=True)
        stacje_url = "https://raw.githubusercontent.com/Ladonean/Nauka/main/Stacje.csv?raw=true"
        location_data = wczytaj_stacje(stacje_url)


        opady_url = f'https://raw.githubusercontent.com/Ladonean/FigDetect/main/o_d_{end_date.strftime("%m")}_{end_date.strftime("%Y")}.csv'
        rain_data = wczytaj_csv(opady_url)
        if rain_data is not None:

            merged_data = merge_data(location_data, rain_data, end_date)

            st.dataframe(merged_data)
            max_value = merged_data['Opady'].astype(float).max()
            min_value = merged_data['Opady'].astype(float).min()
            
            st.write(f"Maksymalna ilość opadów: {max_value}")
            st.write(f"Minimalna ilość opadów: {min_value}")

            path_shp = 'https://raw.githubusercontent.com/Ladonean/FigDetect/main/gadm41_POL_1.shp'
            # Rysowanie mapy
            fig, ax = plot_wynik(path_shp, merged_data, f'Opady {end_date.strftime("%d")}-{end_date.strftime("%m")}-{end_date.strftime("%Y")}')
            st.markdown('<h2 id="polska">Polska</h2>', unsafe_allow_html=True)
            st.pyplot(fig)

    # with st.container():
    #     csv_url = "https://raw.githubusercontent.com/Ladonean/Nauka/main/Stacje.csv?raw=true"
    #     data = load_data(csv_url)
    #     st.dataframe(data)




