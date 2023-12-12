# Imports
import folium
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_folium import st_folium, folium_static
import services.MetroBike_Comm as api_service
import services.RouteCalculation as route_calc
import services.service_declaration as consts
import services.init as init
init.init()

# Page config and title setting
st.set_page_config(
    page_title="Route Planning",
    page_icon="🚲",
    layout="wide"
)


# Title and description
st.title("Route Planning")
st.write("Up for a trip and happy to be taking the bike on a wonderful sunny day? Pick your location and destination and we will find a route for you!")

# Build expander for location picking
locationpick = st.expander("Pick your location", expanded=1)
with locationpick:
    left, right = st.columns(2)
    # left column in expander to select start location
    with left:
        # create folium map with consts, build marker feature group and add existing markers to map
        st.write("### Your location:")
        m = folium.Map(location=consts.CENTER_START, zoom_start=consts.ZOOM_START)
        fg1 = folium.FeatureGroup(name="markers_3")
        for marker in st.session_state["markers_3"]:
            fg1.add_child(marker)

        # bidirectional communication between streamlit and folium through st_folium
        st_data = st_folium(
            m,
            center=st.session_state["center"],
            zoom=consts.ZOOM_START,
            key="route_planning_m3",
            feature_group_to_add=fg1,
            height=400,
            width=700,
        )

        # add marker to feature group, if "last_clicked" property of map is set. delete old marker first
        if st_data["last_clicked"] is not None:
            random_marker = folium.Marker(
                location=[st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]],
                popup="Your location",
            )

            # delete old marker
            st.session_state["markers_3"] = []
            # add new marker
            st.session_state["markers_3"].append(random_marker)

            # add destination to dict route for routing and control of task completion
            st.session_state["route"]["start"] = [st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]]
            
            # display information on selected location
            st.write("You have selected the following coordinates: ")
            st.write(st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"])

    # right column in expander to select destination
    with right:
        st.write("### Select a destination:")
        m2 = folium.Map(location=consts.CENTER_START, zoom_start=consts.ZOOM_START)
        fg2 = folium.FeatureGroup(name="markers_32")
        for marker in st.session_state["markers_32"]:
            fg2.add_child(marker)

        # bidirectional communication between streamlit and folium through st_folium
        st_data2 = st_folium(
            m2,
            center=st.session_state["center"],
            zoom=consts.ZOOM_START,
            key="route_planning_m32",
            feature_group_to_add=fg2,
            height=400,
            width=700,
        )

        # st.write(st_data)
        if st_data2["last_clicked"] is not None:
            random_marker = folium.Marker(
                location=[st_data2["last_clicked"]["lat"], st_data2["last_clicked"]["lng"]],
                popup="Your location",
            )

            # delete old marker
            st.session_state["markers_32"] = []
            # add new marker
            st.session_state["markers_32"].append(random_marker)            
            st.session_state["route"]["end"] = [st_data2["last_clicked"]["lat"], st_data2["last_clicked"]["lng"]]

            # st.write(st.session_state["markers_32"])
            st.write("You have selected the following coordinates: ")
            st.write(st_data2["last_clicked"]["lat"], st_data2["last_clicked"]["lng"])


if len(st.session_state["route"]["start"]) != 0 and len(st.session_state["route"]["end"]) != 0:
    
    # get nearest stations for bike collection from starting point by distance (haversine)
    pickup_station = route_calc.get_station_w_distances("bike",(st.session_state["route"]["start"][0], st.session_state["route"]["start"][1])).iloc[0]
    # get neareset station for bike return from destination by distance (haversine)
    return_station = route_calc.get_station_w_distances("dock", (st.session_state["route"]["end"][0], st.session_state["route"]["end"][1])).iloc[0]

    route = route_calc.get_multi_stop_bike_route([
        st.session_state["route"]["start"],
        pickup_station["geometry"]["coordinates"],
        return_station["geometry"]["coordinates"],
        st.session_state["route"]["end"]
    ])

    # summary for route = {'distance': XX, 'duration': YY} from ORS API
    routesummary = (route["features"][0]["properties"]["summary"])

    # create GeoJSON layer, as route is returned as GeoJSON from API 
    geojson_layer = folium.GeoJson(route)

    # print features
    st.write("### Your journey:")
    
    # display info on automatically-picked locations
    st.write("We have selected the nearest stations around your location and destination. Your route looks like this: ")
    st.write("Pick up a bike at: ", pickup_station["properties"]["name"], " and return it at: ", return_station["properties"]["name"])
    st.write("The total distance of this route will be: ", round(routesummary["distance"] / 1000, 2), "km")

    # Create a Folium map centered at the first point
    m = folium.Map(location=(st.session_state["route"]["start"]), zoom_start=12)

    # Add marker for the second point
    # folium marker start 
    start_marker = folium.Marker(
        st.session_state["route"]["start"],
        popup="Start",
        icon=folium.Icon(prefix='fa', icon="location-arrow", color="red")
    )

    pickup_marker = folium.Marker(
        pickup_station["geometry"]["coordinates"],
        popup="Pickup of Bike",
        icon=folium.Icon(prefix='fa', icon="bicycle", color="red")
    )

    return_marker = folium.Marker(
        return_station["geometry"]["coordinates"],
        popup="End of Bike Rental",
        icon=folium.Icon(prefix='fa', icon="bicycle", color="red")
    )

    end_marker = folium.Marker(
        st.session_state["route"]["end"],
        popup="End of Route",
        icon=folium.Icon(prefix='fa', icon="home", color="red")
    )

    markers = [start_marker, pickup_marker, return_marker, end_marker]

    for marker in markers:
        marker.add_to(m)

    # Add GeoJSON layer to the map
    geojson_layer.add_to(m)

    # Display the map using Streamlit
    folium_static(m)
