import streamlit as st
import services.MetroBike_Comm as services
import services.service_declaration as consts
import services.init as init

# Page config and title setting
st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
    layout="wide"
)

init.init()

st.write("## Metro Bike Share: Los Angeles Bike Stations")
st.write("""
    With over 200 stations, Metro Bike is the most sustainable way to commute around Los Angeles - keeping you healthy and helping the environment at the same time.
    This application is part of a university project in the course "Applied Data Science" at the University of applied sciences in Regensburg, Germany.
    It is the goal to help users find bikes, return them and plan their routes.

    ### How to use this application
    Applicable for finding and returning a bike:    
    - Select the page you want to use in the sidebar on the left.
    - Pick your current location on the map.
    - The application will show you the nearest bike stations.
    - Select a station to start your navigation.
         
    Applicable for planning a route:
    - Pick your current location on the map first.
    - Then pick your destination.
    - The application will show you a possible route and the bike stations on its way.
         
    ### Known Issues with Streamlit
    - The map might not show the pin when you click on the map - move map to update.
    - Selecting a station might not work on the first try - try again.
         
         
    """)