import pandas
import streamlit as st

import services.MetroBike_Comm as services

# streamlit page to show all stations on a map

st.set_page_config(
    page_title="Metrobike stations",
    page_icon="🚲",
    layout="wide"
)


stations = services.get_raw_data()

st.write("""
# Metrobike Stations

This page shows all stations of the Metrobike system in Los Angeles.

""")

map_data_frame = pandas.DataFrame()
# build one column for popup text and "totalDocks" as label
map_data_frame["Docks"] = stations["properties"].apply(lambda x: "Total docks: " + str(x["totalDocks"]))
map_data_frame["Street"] = stations["properties"].apply(lambda x: "Street: " + str(x["addressStreet"]))
# build one column for longitude and one for latitude
map_data_frame["lat"] = stations["geometry"].apply(lambda x: x["coordinates"][0])
map_data_frame["lng"] = stations["geometry"].apply(lambda x: x["coordinates"][1])


st.map(map_data_frame,
       latitude='lat',
       longitude='lng',
       )

st.write("""
### Raw data for interested nerds
""")

st.dataframe(map_data_frame)