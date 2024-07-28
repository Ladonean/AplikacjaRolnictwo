import streamlit as st
import pandas as pd
import openai

page_element="""
<style>
[data-testid="stAppViewContainer"]{
  background-image: url("https://github.com/Ladonean/Nauka/blob/main/nature-fcp.png");
  background-size: cover;
}
</style>
"""

st.markdown(page_element, unsafe_allow_html=True)
st.header('st.write')

# Example 1

st.write('Hello, *World!* :sunglasses:')

# Example 2

st.write(1234)

# Example 3

df = pd.DataFrame({
     'first column': [1, 2, 3, 4],
     'second column': [10, 20, 30, 40]
     })
st.write(df)

st.markdown(page_element, unsafe_allow_html=True)

