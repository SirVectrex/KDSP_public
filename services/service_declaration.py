"""
    This file serves as a global definition of constants used throughout the project.
    They can be used by importing this file and referencing the constant.

    Example:

        from services.service_declaration import METROBIKE_URL
        print(METROBIKE_URL)

"""
# Parameters for calculating distances, time and routes

# MetroBike API URL
METROBIKE_URL = "https://bikeshare.metro.net/stations/json/"

# Earth radius in km
EARTH_RADIUS = 6371.0

# Avg. walking speed of humans in m/s
AVG_WALKING_SPEED = 1.4

# global center of org. maps
CENTER_START = [34.025437, -118.306550]

# global definition of map zoom on initialization
ZOOM_START = 10



