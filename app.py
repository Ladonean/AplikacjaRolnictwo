import streamlit as st
import pandas as pd

def load_css(file):
  with open(file) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

st.title("moja apka")
