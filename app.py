import streamlit as st
import base64

# Funkcja do załadowania obrazu tła
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png" or "jpg"};base64,{encoded_string.decode()});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            opacity: 0.5;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Dodaj tło z lokalnego pliku
add_bg_from_local('R.jpg')

# Reszta kodu Streamlit
st.title("Moja aplikacja Streamlit z tłem")
st.write("Przykładowa zawartość aplikacji")
