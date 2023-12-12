# Imports
import folium
import streamlit as st
from streamlit_folium import st_folium, folium_static
import services.MetroBike_Comm as api_service
import services.RouteCalculation as route_calc
import services.service_declaration as consts
import services.init as init
init.init()

# Page config and title setting
st.set_page_config(
    page_title="Return a Bike",
    page_icon="🚲",
    layout="wide"
)



# reset map 

stations = []
stationpick = None
locationpick = st.expander("Pick your location", expanded=1)

# Build expander for location picking
with locationpick:
    left, right = st.columns(2)
    # left column in expander to select current location of user
    with left:
        # create folium map with consts, build marker feature group and add existing markers to map
        m = folium.Map(location=consts.CENTER_START, zoom_start=consts.ZOOM_START)
        fg = folium.FeatureGroup(name="markers_2")
        for marker in st.session_state["markers_2"]:
            fg.add_child(marker)

        # bidirectional communication between streamlit and folium through st_folium
        st_data = st_folium(
            m,
            center=st.session_state["center"],
            zoom=consts.ZOOM_START,
            key="return_a_bike",
            feature_group_to_add=fg,
            height=400,
            width=700,
        )

        # st.write(st_data)
        if st_data["last_clicked"] is not None:
            # add marker to feature group, if "last_clicked" property of map is set. delete old marker first
            random_marker = folium.Marker(
                location=[st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]],
                popup="Your location",
            )
            # delete old marker
            st.session_state["markers_2"] = []
            # add new marker
            st.session_state["markers_2"].append(random_marker)

    with right:
        st.title("Return a bike")
        st.write(
            "Please click on a location on the map and then select 'Show pin' to your location. When happy with your "
            "location, please click on 'Find Bikes' and we will take care of the rest")

        st.write("Interest to see, where we have our bike stations?")
        st.markdown('<a href="/Metro_Bike_Stations" target="_self">View all</a>', unsafe_allow_html=True)

        if st_data["last_clicked"] is not None:
            st.write("You have selected the following coordinates: ")
            st.write(st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"])

if st_data["last_clicked"] is None:
    # reset markers on map
    st.session_state["markers_2"] = []


if st_data["last_clicked"] is not None:
    st.session_state["center"] = [st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]]

    # get stations with distance to selected location
    stations = route_calc.get_station_w_distances("dock",(st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]))

    # show stations in expander
    destinationlist = st.expander("Select your destination", expanded=1)
    with destinationlist:
            # slider for number of stations displayed
            st.write("Docks available at station")

            # show table with stations and distances to selected location but only show slider selected amount
            for i in range(0, st.slider("Number of stations displayed", 1, 10, 5, 1)):
                with st.container():
                    col1, col2, col3 = st.columns([1, 1, 1])
                    # button to select station
                    with col1:
                        if st.button("Select station", key=i):
                            stationpick = stations.iloc[i]
                    with col2:
                        st.write("Free docks: ", stations.iloc[i]["properties"]["docksAvailable"], " / ", stations.iloc[i]["properties"]["totalDocks"])
                    with col3:
                        st.write(round(stations.iloc[i]["distance"], 2), "km")
    # st.dataframe(stations)


if stationpick is not None:

    route = route_calc.get_route_calculation_foot(
        (stationpick["geometry"]["coordinates"][0],stationpick["geometry"]["coordinates"][1]),
        (st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]))

    geojson_layer = folium.GeoJson(route)


    st.write("### Your route to bike dropoff:")
    col1, col2 = st.columns([3, 1])
    with col1:
        # Create a Folium map centered at the first point
        m = folium.Map(location=(st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]), zoom_start=15)

        # Add marker for the first point
        folium.Marker(
            (stationpick["geometry"]["coordinates"][0],stationpick["geometry"]["coordinates"][1]), popup="Destination", icon=folium.Icon(color="red", prefix="fa", icon="home" )
        ).add_to(m)

        # Add marker for the second point
        folium.Marker(
            (st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]), popup="Your location", icon=folium.Icon(prefix='fa', icon="location-arrow", color="red")
        ).add_to(m)

        # Add GeoJSON layer to the map
        geojson_layer.add_to(m)

        # Display the map using Streamlit
        folium_static(m)

    with col2:
            st.write("You have selected the following station: ")
            st.write(stationpick["properties"]["name"])
            st.write("Distance: ", round(stationpick["distance"], 2), "km")
            st.write("Address: ", stationpick["properties"]["addressStreet"])
            st.write("Minutes away: ", route_calc.get_walking_time(stationpick["distance"]))
            st.write("Docks available: ", stationpick["properties"]["docksAvailable"], " / ", stationpick["properties"]["totalDocks"])
            # st.write(stationpick)

