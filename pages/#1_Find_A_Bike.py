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
    page_title="Find a Bike",
    page_icon="🚲",
    layout="wide"
)



stations = []
stationpick = None

# Build expander for location picking
locationpick = st.expander("Pick your location", expanded=1)
with locationpick:
    left, right = st.columns(2)
    # left column in expander to select current location of user
    with left:
        # create folium map with consts, build marker feature group and add existing markers to map
        m = folium.Map(location=consts.CENTER_START, zoom_start=consts.ZOOM_START)
        fg = folium.FeatureGroup(name="markers_1")
        for marker in st.session_state["markers_1"]:
            fg.add_child(marker)

        # bidirectional communication between streamlit and folium through st_folium
        st_data = st_folium(
            m,
            center=st.session_state["center"],
            zoom=consts.ZOOM_START,
            key="new",
            feature_group_to_add=fg,
            height=400,
            width=700,
        )

        # add marker to feature group, if "last_clicked" property of map is set. delete old marker first
        if st_data["last_clicked"] is not None:
            location_selected = folium.Marker(
                location=[st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]],
                popup="Your location",
            )
            # delete old marker
            st.session_state["markers_1"] = []
            # add new marker
            st.session_state["markers_1"].append(location_selected)
            
    # right column in expander
    with right:
        # display information and instructions
        st.title("Find a bike")
        st.write(
            "Please click on a location on the map and then select 'Show pin' to your location. When happy with your "
            "location, please click on 'Find Bikes' and we will take care of the rest")

        # button to get location by Browser API - of limited use when not in US but a simple component to implement - irreversable if clicked
        location = streamlit_geolocation()
        # if button pressed - set location and marker on map
        if location["latitude"] is not None:
            location_coord = [location["latitude"], location["longitude"]]
            st.session_state["center"] = location_coord
            st.session_state["zoom"] = 15
            # delete old marker
            st.session_state["markers_1"] = []
            # add marker and append to feature group
            random_marker = folium.Marker(
                location=location_coord,
                popup="Your location",
            )
            st.session_state["markers_1"].append(random_marker)

            # add location to last_clicked
            st_data["last_clicked"] = {"lat": location["latitude"], "lng": location["longitude"]}


        # link to all bike stations page
        st.write("Interest to see, where we have our bike stations?")
        st.markdown('<a href="/Metro_Bike_Stations" target="_self">View all</a>', unsafe_allow_html=True)

        # display coordinates of selected location (if selected)
        if st_data["last_clicked"] is not None:
            st.write("You have selected the following coordinates: ")
            st.write(st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"])


if st_data["last_clicked"] is None:
    # reset markers on map
    st.session_state["markers_1"] = []


# display only if location is selected
if st_data["last_clicked"] is not None:
    st.session_state["center"] = [st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]]
    
    #move map to selected location


    # get stations with distance to selected location
    stations = route_calc.get_station_w_distances("bike", (st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]))

    # show stations in expander
    destinationlist = st.expander("Select your destination", expanded=1)
    with destinationlist:
            # if no station is within 100km of selected location - show warning and do not show table or proceed with task
            if (stations.iloc[0]["distance"] > 100):
                st.warning("No stations within 100km of your location. MetroBike is only available in Los Angeles.")
            else: 
                # slider for number of stations displayed
                st.write("Bikes available at station")

                # show table with stations and distances to selected location but only show slider selected amount
                for i in range(0, st.slider("Number of stations displayed", 1, 10, 5, 1)):
                    with st.container():
                        col1, col2, col3 = st.columns([1, 1, 1])
                        # button to select station
                        with col1:
                            # button to select station for route calculation
                            if st.button("Select station", key=i):
                                stationpick = stations.iloc[i]
                        with col2:
                            # show #available bikes at station
                            st.write("Bikes: ", stations.iloc[i]["properties"]["bikesAvailable"])
                        with col3:
                            # show distance to selected location
                            st.write(round(stations.iloc[i]["distance"], 2), "km")

# display section only if station is selected through buttons in table above
if stationpick is not None:
    # request walkable route calculation from Route module - using selected station and location of user as input
    route = route_calc.get_route_calculation_foot(
        (stationpick["geometry"]["coordinates"][0],stationpick["geometry"]["coordinates"][1]),
        (st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]))

    # create GeoJSON layer, as route is returned as GeoJSON from API 
    geojson_layer = folium.GeoJson(route)

    st.write("### Your route to your next bike:")
    
    # create columns for displaying map and route information
    col1, col2 = st.columns([3, 1])
    with col1:
        # Create a Folium map centered at the first point
        m = folium.Map(location=(st_data["last_clicked"]["lat"], st_data["last_clicked"]["lng"]), zoom_start=15)

        # Add marker for the first point
        folium.Marker(
            (stationpick["geometry"]["coordinates"][0],stationpick["geometry"]["coordinates"][1]), popup="Destination", icon=folium.Icon(color="red", prefix="fa", icon="bicycle")
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
        # display route information
            st.write("You have selected the following station: ")
            st.write(stationpick["properties"]["name"])
            st.write("Distance: ", round(stationpick["distance"], 2), "km")
            st.write("Address: ", stationpick["properties"]["addressStreet"])
            st.write("Minutes away: ", route_calc.get_walking_time(stationpick["distance"]))
            st.write("Bikes available: ", stationpick["properties"]["bikesAvailable"])
            # st.write(stationpick)

