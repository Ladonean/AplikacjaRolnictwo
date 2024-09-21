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
import re
from matplotlib.colors import LinearSegmentedColormap

# st.set_page_config(
#     page_title="Aplikacja Rolnictwo",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'About': "https://github.com/Ladonean/Nauka/tree/main"
#     }
# )


json_data = st.secrets["json_data"]
service_account = st.secrets["service_account"]

json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)
# Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)

# ee.Authenticate() 
# ee.Initialize(project='ee-ladone')

def is_coordinates(address):
    pattern = r"Latitude:\s*(-?\d+\.\d+)\s*Longitude:\s*(-?\d+\.\d+)"
    match = re.match(pattern, address)
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        return [latitude, longitude]
    return None

# Funkcja do geokodowania adresu
def geocode_address(address):
    coords = is_coordinates(address)
    if coords:
        return coords
        
    geolocator = Photon(user_agent="app",timeout=10)
    try:
        location = geolocator.geocode(address)
        if location:
            return [location.latitude, location.longitude]
        else:
            return None
    except GeocoderTimedOut:
        return None

def get_image(start_date, end_date, coords, buffer_radius):
    # Pobieranie kolekcji obrazów Landsat 8 (Collection 2 Level 2)

    point = ee.Geometry.Point([coords[1], coords[0]])
    buffer = point.buffer(buffer_radius)
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .filterBounds(buffer)
    
    # Zamiast median(), wybierz pierwszy obraz w kolekcji
    image = collection.median()
    
    # Pobranie daty obrazu
    image_date = image.get('system:time_start').getInfo()
    
    if image_date is not None:
        image_date = datetime.fromtimestamp(image_date / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
    else:
        image_date = "Brak dostępnej daty"
    
    return image, image_date, buffer

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
        (rain_data['Miesiąc'] == selected_date.month)
    ]
    location_data['Stacja'] = location_data['Stacja'].str.strip()
    rain_data_filtered.loc[:, 'Stacja'] = rain_data_filtered['Stacja'].str.strip()
    merged_data = location_data.merge(rain_data_filtered, on='Stacja', how='inner')

    merged_data['Opady'] = pd.to_numeric(merged_data['Opady'], errors='coerce')
    merged_data = merged_data.groupby('Stacja').agg({
        'Opady': 'sum',                # Sumuj wartości opadów
        'X': 'first',
        'Y': 'first',
        'Rok': 'first',
        'Miesiąc': 'first',   

    }).reset_index()
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
    colors = [(0, "yellow"), (0.1, "lightyellow"), (0.2, "#d9ffdb"), (0.4, "#bfffd1"), (0.6, "lightblue"), (1, "blue")]  # (wartość, kolor)
    my_cmap = LinearSegmentedColormap.from_list("my_cmap", colors)
    cbar = ax.contourf(X_siatka, Y_siatka, Z_siatka, cmap=my_cmap, levels=np.arange(0, 120, 10), extend = 'max')
    cax = fig.add_axes([0.93, 0.134, 0.02, 0.72])
    colorbar = plt.colorbar(cbar, cax=cax, orientation='vertical')

    ax.grid(lw=0.3)
    ax.set_title(title, fontweight='bold', pad=15)

    return fig, ax

# Główna funkcja uruchamiająca aplikację
def main():

    with st.sidebar:
        st.title("Aplikacja Rolnictwo")
        st.subheader("Menu:")
        st.markdown(
            """
                - [Mapa](#mapa)
                - [Opady](#opady)
                - [Polska](#polska)
                - [Infromacje](#informacje)
                - [Samouczek](#samouczek)
            """)

    with st.container():
        st.title("Aplikacja Rolnictwo")
        st.markdown("Aplikacja służąca do sprawdzania wskaźnika NDVI i NDWI, a także miesięcznych opadów na obszarze Polski")

    with st.container():
        date = st.date_input("Wybierz datę", value=datetime.today())
        start_date = date.replace(day=1)
        _, last_day = calendar.monthrange(date.year, date.month)
        end_date = date.replace(day=last_day)



    with st.container():

        st.markdown('<h2 id="mapa">Mapa</h2>', unsafe_allow_html=True)
        address = st.text_input("Wpisz adres:", "Czaple, Kartuzy")
        coords = geocode_address(address)
        
        buffer_radius = st.slider('Wybierz promień buffera (w metrach):', min_value=100, max_value=5000, value=1000, step=100)


        if coords:
            if st.button("Aktualizuj mapę"):
                # Pobierz obraz i inne dane
                image, image_date, buffer = get_image(start_date, end_date, coords, buffer_radius)

                # Obliczanie NDVI i NDWI dla wybranego obrazu
                ndvi_image = image.normalizedDifference(['B8', 'B4']).rename('NDVI').clip(buffer)
                ndwi_image = image.normalizedDifference(['B3', 'B8']).rename('NDWI').clip(buffer)

                # Stworzenie warstw do mapy
                ndvi_map_id_dict = geemap.ee_tile_layer(
                    ndvi_image,
                    vis_params={
                        'min': -1,
                        'max': 1,
                        'palette': [
                            'blue',
                            'lightblue',
                            'white',
                            'green',
                            'darkgreen'
                        ]
                    },
                    name="NDVI"
                )

                
                ndwi_map_id_dict = geemap.ee_tile_layer(
                    ndwi_image,
                    vis_params={
                        'min': -1,
                        'max': 1,
                        'palette': [
                            'red',
                            'yellow',
                            'white',
                            'blue',
                            'darkblue'
                        ]
                    },
                    name="NDWI"
                )

                # Stworzenie mapy Folium
                m = folium.Map(location=coords, zoom_start=14, tiles="Esri.WorldImagery")
                folium.Marker(
                    location=coords,
                    popup=address,
                ).add_to(m)

                m.add_child(ndvi_map_id_dict)
                m.add_child(ndwi_map_id_dict)

                folium.LayerControl().add_to(m)
                st.session_state['map'] = m
                m.add_child(folium.LatLngPopup())


        # Wyświetlanie mapy ze stanu sesji
        if 'map' in st.session_state:
            st_folium(st.session_state['map'], width=400, height=400)
        else:
            st.write("Nie udało się zlokalizować adresu.")

                        # Eksport mapy
        if st.button("Eksportuj mapę"):
                    m = st.session_state['map']
                    m.save("Mapa_123.html")
                    st.success("Mapa została zapisana jako Mapa_123.html")
                    with open("Mapa_123.html", "r", encoding="utf-8") as file:
                        html_data = file.read()
                        st.download_button(label="Pobierz mapę", data=html_data, file_name="Mapa_123.html", mime="text/html")



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
            fig, ax = plot_wynik(path_shp, merged_data, f'Opady {end_date.strftime("%m")}-{end_date.strftime("%Y")}')
            st.markdown('<h2 id="polska">Polska</h2>', unsafe_allow_html=True)
            st.pyplot(fig)

    with st.container():
        st.markdown('<h2 id="informacje">Informacje</h2>', unsafe_allow_html=True)
        st.write(""" Po wybraniu adresu i interesującej daty należy nacisnąć przycisk Aktualizuj Mapę.
                     """)
        
        if st.button("NDVI - Normalized Difference Vegetation Index"):
            st.write("""
                    Znormalizowany różnicowy wskaźnik wegetacji to wskaźnik stosowany w pomiarach teledetekcyjnych, pozwalający określić stan rozwojowy oraz kondycję roślinności. NDVI pozwala zdefiniować i zwizualizować obszary porośnięte roślinnością, a także wykryć nieprawidłowe zmiany w procesie wzrostu roślin.
                    Jego wartości skorelowane są z ilością biomasy i zawartością chlorofilu. Do obliczenia wskaźnika NDVI wykorzystuje się wartości odbicia w zakresie czerwonym światła widzialnego oraz bliskiej podczerwieni. 
                    Wartości wskaźnika NDVI zawierają się w zakresie od -1 do 1. Wartości wskaźnika NDVI zbliżone do -1 występują na obszarach pokrytych wodą. Wartości z zakresu od -0,1 do 0,1 występują na obszarach odkrytej gleby bez pokrywy roślinnej. 
                    Wartości wskaźnika NDVI z zakresu od 0,2 do 0,4 są charakterystyczne dla obszarów pokrytych roślinnością będącą w początkowej fazie rozwoju lub słabej kondycji. 
                    Wartości wskaźnika NDVI >0.6 uznawane są za wskaźnik zdrowej roślinności o wysokiej witalności. 
                    Natomiast NDVI zbliżone do 1 są charakterystyczne dla roślin będących w najwyższej fazie rozwoju, w bardzo dobrym stanie zdrowotnym
                    """)
            image = Image.open("NDVI.png")
            st.image(image, caption="Źródło własne", use_column_width=True)
        
        if st.button("NDWI - Normalized Difference Water Index"):
            st.write("""
                    Wskaźnik NDWI służy do monitorowania zmian związanych z zawartością wody w zbiornikach wodnych. 
                    Ponieważ zbiorniki wodne silnie absorbują światło w widzialnym i podczerwonym spektrum elektromagnetycznym, NDWI wykorzystuje pasma zielone i bliskiej podczerwieni, aby wyodrębnić zbiorniki wodne. 
                    Wskaźnik ten jest czuły na tereny zurbanizowane, co może prowadzić do przeszacowania obszarów wodnych.
                    NDWI oblicza się przy użyciu obrazów satelitarnych, które rejestrują zarówno bliską podczerwień (NIR), jak i długości fal zielonych (G). Do oceny stanu środowiska przydatne mogą być również wskaźniki wodne, które mogą wskazać przyczynę gorszej kondycji roślinności wynikającą z deficytu lub nadmiaru wody. 
                    Do najbardziej popularnych należy wskaźnik NDWI, czyli znormalizowany różnicowy wskaźnik wody (Normalized Difference Water Index; Gao 19964) informujący o stanie (zmianach) zawartości wody (absorpcja promieniowania SWIR) i miękiszu gąbczastego w koronach roślinnych (NIR).
                     """)
            image = Image.open("NDWI.png")
            st.image(image, caption="Źródło własne", use_column_width=True)
            
    with st.container():
        st.markdown('<h2 id="samouczek">Samouczek</h2>', unsafe_allow_html=True)
        st.write(""" Po wybraniu adresu i interesującej daty należy nacisnąć przycisk Aktualizuj Mapę.
                     """)


# Uruchomienie aplikacji
if __name__ == "__main__":
    main()
