import streamlit as st
import pandas as pd
import openai


st.header('st.write')
st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://github.com/Ladonean/Nauka/blob/main/nature-fcp.png")
    }
    """,
    unsafe_allow_html=True
)

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

