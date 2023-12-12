import math
import requests
import services.service_declaration as consts
import services.MetroBike_Comm as api_service
import streamlit as st


def add_distances_to_dataframe(df, coordinates):
    """
    Add distance to a given coordinate to a dataframe.

    Parameters:
    - df: Pandas Dataframe with Station data - coordinates in geometry "coordinates
    - coordinates: Tuple (latitude, longitude) in decimal degrees

    Returns:
    - Pandas Dataframe with Station data and additional column "distance"
    """
    df = df.assign(
    distance=df.apply(
        lambda x: get_distance_great_circle(coordinates, (x["geometry"]["coordinates"][0], x["geometry"]["coordinates"][1])),
        axis=1
    )
)
    return df


def get_distance_great_circle(coord1, coord2):
    """
    Calculate the great-circle distance between two coordinates on the Earth's surface. Will not use any API credits.
    
    Parameters:
    - coord1: Tuple (latitude1, longitude1) in decimal degrees
    - coord2: Tuple (latitude2, longitude2) in decimal degrees
    
    Returns:
    - Distance in kilometers
    """

    # Convert decimal degrees to radians
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = consts.EARTH_RADIUS * c

    return distance


def get_walking_distance(coord1, coord2):
    """
    Calculate the walking distance between two coordinates using the OpenRouteService API.
    
    Parameters:
    - coord1: Tuple (latitude1, longitude1) in decimal degrees
    - coord2: Tuple (latitude2, longitude2) in decimal degrees
    
    Returns:
    - Distance in meters
    
    """
    # url for API call with foot_walking profile
    base_url = "https://api.openrouteservice.org/v2/directions/foot-walking"

    # parameters for API call


    route = [
        [coord1[1], coord1[0]], [coord2[1], coord2[0]]
    ]

    body = {"coordinates": route}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': st.secrets["ors_key"],
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post('https://api.openrouteservice.org/v2/directions/foot-walking/geojson', json=body, headers=headers)

    # test if request was successful and return distance
    if call.status_code == 200:
        data = call.json()
        distance = data["features"][0]["properties"]["segments"][0]["distance"]

        return distance
    else:
        print(f"Error: {call.status_code}")
        print(call.text)
        return None


def get_walking_time(distance):
    """
    Calculate walking time based on distance and average walking speed. Will not use any API credits.
    
    Parameters:
    distance: Distance in kilometers
    
    Constants:
    walking_speed: Average walking speed in meters per second

    Returns:
    Walking time in Minutes (ceiled)
    """
    # convert kilometers to meters
    distance = distance * 1000
    time = distance / consts.AVG_WALKING_SPEED
    return math.ceil(time / 60)


def get_route_calculation_foot(coord1, coord2):
    """
    Calculate a specifc route from coordinate a to coordinate b for walking.
    
    Parameters:
    - coord1: Tuple (latitude1, longitude1) in Dezimalgrad
    - coord2: Tuple (latitude2, longitude2) in Dezimalgrad
    
    Returns:
    - GeoJson with route
    """

    route = [
        [coord1[1], coord1[0]], [coord2[1], coord2[0]]
    ]

    body = {"coordinates": route}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': st.secrets["ors_key"],
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post('https://api.openrouteservice.org/v2/directions/foot-walking/geojson', json=body, headers=headers)

    # print(call.status_code, call.reason)
    # print(call.text)

    if call.status_code == 200:
        data = call.json()
        return data
    else:
        print(f"Error: {call.status_code}")
        return None


def get_route_calculation_bike(coord1, coord2):
    """
    Calculate a specifc route from coordinate a to coordinate b for biking.
    
    Parameters:
    - coord1: Tuple (latitude1, longitude1) in Decimal
    - coord2: Tuple (latitude2, longitude2) in Decimal
    
    Returns:
    - List of coordinates on route [(lat1, lon1), (lat2, lon2), ...]
    """
    base_url = "https://api.openrouteservice.org/v2/directions/cycling-regular"

    params = {
        "api_key": st.secrets["ors_key"],
        "coordinates": [coord1, coord2],
        "units": "meters",
        "profile": "cycling-regular",
    }

    response = requests.post(base_url, json=params)

    if response.status_code == 200:
        data = response.json()
        geometry = data["features"][0]["geometry"]["coordinates"]
        return geometry
    else:
        print(f"Error: {response.status_code}")
        return None


def get_multi_stop_bike_route(coords):
    """
    Calculate a route between multiple stops for biking.
    
    Parameters:
    - coords: List of tuples [(lat1, lon1), (lat2, lon2), ...] of coordinates that are part of the route
    
    Returns:
    - GeoJSON
    """

    # flip lat and long in coordinates for each element in array
    for i in range(len(coords)):
        coords[i] = [coords[i][1], coords[i][0]]

    body = {"coordinates": coords}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': st.secrets["ors_key"],
        'Content-Type': 'application/json; charset=utf-8'
    }
    call = requests.post('https://api.openrouteservice.org/v2/directions/foot-walking/geojson', json=body, headers=headers)

    # print(call.status_code, call.reason)
    # print(call.text)

    if call.status_code == 200:
        data = call.json()
        return data
    else:
        print(f"Error: {call.status_code}")
        print(call.text)
        return None
    
def get_station_w_distances(mode_switch,coord):
    """
    Get all stations and add distance to a given coordinate.
    
    Parameters:
    - coord: Tuple (latitude, longitude) in Decimal
    - mode_switch: String "bike" or "dock" to switch between stations with bikes or empty docks
    
    Returns:
    - Pandas Dataframe with Station data and additional column "distance" sorted by distance (asc) in kilometers
    """
    if mode_switch == "bike":
        # get raw data
        stations = api_service.get_stations_with_bikes()
    elif mode_switch == "dock":
        # get raw data
        stations = api_service.get_stations_with_empty_racks()
        
    # add distances (approximation) to dataframe
    stations = add_distances_to_dataframe(stations,coord)
    # sort stations by distance (asc)
    stations = stations.sort_values(by=['distance'])

    return stations

def get_address(coord):
    """
    Get address for a given coordinate.
    
    Parameters:
    - coord: Tuple (latitude, longitude) in Decimal
    
    Returns:
    - Address as String
    """
    # url for API call with foot_walking profile
    base_url = "https://api.openrouteservice.org/geocode/reverse"

    # parameters for API call
    params = {
        "api_key": st.secrets["ors_key"],
        "point.lon": coord[1],
        "point.lat": coord[0],
        "size": 1,
        "layers": "address"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        address = data["features"][0]["properties"]["label"]
        return address
    else:
        print(f"Error: {response.status_code}")
        return None
