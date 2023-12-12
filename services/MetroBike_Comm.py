import json
import pandas as pd
import streamlit as st
from urllib.request import Request, urlopen
import services.service_declaration as consts
from datetime import datetime


if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = {
        "lastupdated": None,
        "data": None
    }


def get_raw_data():
    # check if data is cached and not older than 10 minutes
    if st.session_state["raw_data"]["data"] is not None and (datetime.now() - st.session_state["raw_data"]["lastupdated"]).total_seconds() < 600:
        print("LOG: Using cached data")
        return st.session_state["raw_data"]["data"]

    
    # get request to url to get raw data
    req = Request(consts.METROBIKE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    response = response.decode().replace("'", '"')
    data = json.loads(response)

    # convert to pandas dataframe
    df = pd.DataFrame(data['features'])
    df.drop('type', axis=1, inplace=True)

    # lat and lng are flipped in data frame at this point - fix this
    df['geometry'] = df['geometry'].apply(lambda x: {'type': x['type'], 'coordinates': x['coordinates'][::-1]})

    # save data to cache
    st.session_state["raw_data"]["data"] = df
    st.session_state["raw_data"]["lastupdated"] = datetime.now()

    return df


def get_stations_with_bikes():
    """
    Get live dataset of active bike stations and their amount of free bikes. Will delete all stations with no free bikes.
    Returns:
    - Pandas Dataframe with Station data
    """

    df = get_raw_data()

    # filter out stations with no bikes
    df = df[df['properties'].apply(lambda x: x['bikesAvailable'] > 0)]

    
    return df


def get_stations_with_empty_racks():
    """
    Get live dataset of active bike stations, that have empty racks. Will delete all stations with no free bike racks.
    Returns:
    - Pandas Dataframe with Station data
    """

    df = get_raw_data()

    # filter out stations with no empty racks
    df = df[df['properties'].apply(lambda x: x['docksAvailable'] > 0)]


    return df

