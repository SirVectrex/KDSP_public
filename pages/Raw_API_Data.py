import streamlit as st
import pandas as pd
import services.MetroBike_Comm as mb

# streamlit page configuration
st.set_page_config(
    page_title="MetroBike",
    page_icon="🚲",
    layout="wide"
)

st.write("""
# MetroBike
A Streamlit app to visualize MetroBike data
""")

data = mb.get_raw_data()

# display raw data
st.write("""
## Raw Data from MetroBike API
""")

st.dataframe(data)

