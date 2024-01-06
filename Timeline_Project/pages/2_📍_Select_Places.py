"""
This file is for the graphs and charts page of the Timeline Project, which will eventually create
interactive plotly plots visualizing the placeVisits data over time as well as other relationships.
"""


# MODULARIZE THIS PAGE!!!!!!!!


import streamlit as st
import folium
from streamlit_folium import st_folium
from sys import path
# Enables importable_file to be imported
path.append('Timeline_Project')
from importable_file import create_sidebar, add_place_to_active_selections


st.set_page_config(page_title="Timeline Analyzer", page_icon="🗺️", layout="centered")


def vertical_line(n):
    """Inserts n lines of vertical space."""
    for i in range(n):
        st.write('')


def create_map():
    """Creates the map of all selectable lat/long locations, and returns the map object to be used with st.folium()."""

    # Creates map and tile layers (does satellite first to make it default)
    esri_tile = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr='Esri Satellite',
        name='Satellite Map',
    )
    m = folium.Map(zoom_start=5, location=[50, -120], tiles=esri_tile)
    folium.TileLayer('openstreetmap', attr='Open Street Map', name='Open Street Map').add_to(m)
    folium.TileLayer('hikebike', attr='stamenwatercolor', name='Terrain Map').add_to(m)
    folium.LayerControl().add_to(m)

    # Creates markers
    i = 0
    #folium.Marker([47.222549, -120.5495964], popup='Click me').add_to(m)
    for lat_long_tuple in st.session_state.unique_lists_dict['lat_longs']:
        if i < 100:
            folium.Marker(lat_long_tuple, popup=f'latitude={lat_long_tuple[0]}\nlongitude={lat_long_tuple[1]}', icon=
            folium.Icon(icon='star', color=st.session_state.settings_dict['map_marker_color'])).add_to(m)
            i+=1
    return m


if st.session_state.data_processed:
    st.write('### 📍 Select what places you want to include!')
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        address = st.selectbox('', ['Search for addresses here:'] + st.session_state.unique_lists_dict['addresses'])
        place_name = st.selectbox('', ['Search for place names here:'] + st.session_state.unique_lists_dict['names'])
    with col2:
        vertical_line(2)
        # Ensures that the current address hasn't already been selected and isn't the guideline selection
        if st.button('Add address') and address not in st.session_state.added_locations_dict['addresses'] and \
                address != 'Search for addresses here:':
            st.session_state.added_locations_dict['addresses'].append(address)
            st.session_state.active_selections.append(address)
            add_place_to_active_selections()

        vertical_line(2)

        if st.button('Add place name') and place_name not in st.session_state.added_locations_dict['place_names'] and \
                place_name != 'Search for place names here:':
            st.session_state.added_locations_dict['place_names'].append(place_name)
            st.session_state.active_selections.append(place_name)
            add_place_to_active_selections()
        else:
            st.session_state.place_added = False

    vertical_line(1)
    st.write('Or you can select points on the map here:')
    m = create_map()
    clicked_markers = st_folium(m, width=700, height=500, returned_objects=['last_object_clicked'])

    # If the last marker clicked is not empty, it grabs the lat long into that was clicked and only adds (as a tuple) to
    # the active_selections and added_locations dicts if it's not already there (that's the second if statement)
    if clicked_markers['last_object_clicked'] is not None:
        last_clicked_lat_long = (clicked_markers['last_object_clicked']['lat'],
                                 clicked_markers['last_object_clicked']['lng'])

        if last_clicked_lat_long not in st.session_state.added_locations_dict['lat_longs']:
            st.session_state.added_locations_dict['lat_longs'].append(last_clicked_lat_long)
            st.session_state.active_selections.append(last_clicked_lat_long)
            add_place_to_active_selections()

    create_sidebar()
else:
    st.write('#### Upload your Google Takeout file to begin!')



