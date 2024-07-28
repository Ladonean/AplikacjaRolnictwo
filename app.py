import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

                col1,col2 = st.columns(2)
                
                # Creating a 2 days delay for the date_input placeholder to be sure there are satellite images in the dataset on app start
                today = datetime.today()
                delay = today - timedelta(days=5)

                # Date input widgets
                col1.success("Data P 📅")
                initial_date = col1.date_input("initial", value=delay, label_visibility="collapsed")





# Run the app
if __name__ == "__main__":
    main()
