import services.service_declaration as consts
import streamlit as st


def init():

    if "raw_data" not in st.session_state:
        st.session_state["raw_data"] = {
            "lastupdated": None,
            "data": None
        }

        # Setup global definitions if needed (e.g. for map center, zoom, markers, etc.)
    if "center" not in st.session_state:
        st.session_state["center"] = consts.CENTER_START
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = consts.ZOOM_START
    if "markers_1" not in st.session_state:
        st.session_state["markers_1"] = []

        # Setup global definitions if needed (e.g. for map center, zoom, markers, etc.)
    if "center" not in st.session_state:
        st.session_state["center"] = consts.CENTER_START
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = consts.ZOOM_START
    if "markers_2" not in st.session_state:
        st.session_state["markers_2"] = []


            # Setup global definitions if needed (e.g. for map center, zoom, markers, etc.)
    if "center" not in st.session_state:
        st.session_state["center"] = consts.CENTER_START
    if "zoom" not in st.session_state:
        st.session_state["zoom"] = consts.ZOOM_START
    if "markers_3" not in st.session_state:
        st.session_state["markers_3"] = []
    if "markers_32" not in st.session_state:
        st.session_state["markers_32"] = []
    # add route dict as global definition to save start and end coordinates beyond map reloads
    if "route" not in st.session_state:
        st.session_state["route"] = {
            "start": [],
            "end": []
        }


