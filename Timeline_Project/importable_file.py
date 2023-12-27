"""
This file can be used to create and import functions from, since file names with emojis are not valid identifiers;
however, with Streamlit's multipage system, the page name must be the file name, so I want to keep the emojis.
"""
import streamlit as st
import pandas as pd


def get_place_df(place):
    """
    Creates the dataframe for one location, and adds it to the session state dictionary.
    place - an address, place name, or lat long tuple from active_selections
    Essentially just loops through every row in place_vists_df and checks if the place is that row's address, name,
    or lat long tuple.
    If it does, it appends the entire row to a list, which is converted to a DataFrame and added to
    active_places_df_dict.
    """
    place_list = []
    # Creates just one tz object and passes it into adjust_timezone() to save lots of time
    for row in st.session_state.place_visits_df.itertuples():
        # This is the old code that worked, but I'm fairly confident I cleaned its up correctly.
        # If things regarding making the dataframes off of selected places start breaking, try restoring this code!

        # if place in st.session_state.added_locations_dict['addresses'] and place == row.address:
        #     place_list.append([row.latitudeE7, row.longitudeE7, row.address, row.name,
        #     row.startTimestamp, row.endTimestamp, row.duration])
        # elif place in st.session_state.added_locations_dict['place_names'] and place == row.name:
        #     place_list.append([row.latitudeE7, row.longitudeE7, row.address, row.name,
        #     row.startTimestamp, row.endTimestamp, row.duration])
        # elif place in st.session_state.added_locations_dict['lat_longs'] and
        #   place == (row.latitudeE7, row.longitudeE7):
        #     place_list.append([row.latitudeE7, row.longitudeE7, row.address, row.name,
        #     row.startTimestamp, row.endTimestamp, row.duration])
        if place == row.address or place == row.name or place == (row.latitudeE7, row.longitudeE7):
            place_list.append(
                [row.latitudeE7, row.longitudeE7, row.address, row.name,
                 row.startTimestamp, row.endTimestamp, row.duration])
    place_df = pd.DataFrame(place_list, columns=['latitudeE7', 'longitudeE7', 'address', 'name', 'startTimestamp', 'endTimestamp', 'duration'])
    st.session_state.active_places_df_dict[place] = place_df


def add_place_to_active_selections():
    """
    Empties the active places dict so that it can be rebuilt using only the current selections (if you don't
    empty, then nothing could ever be deleted even if the user unselects a location), and reruns so that pages can
    dynamically update to the new selections.
    """
    st.session_state.active_places_df_dict = {}
    for place in st.session_state.active_selections:
        get_place_df(place)
    st.experimental_rerun()


def create_multiselect():
    """Creates the multiselect in the sidebar and handles adding selections to the active_places_df_dict."""

    # Uses session_state.active_selections to update and set the default selections to avoid losing them on reload
    num_able_to_select = len(st.session_state.added_locations_dict["addresses"]) + \
                         len(st.session_state.added_locations_dict["place_names"]) + \
                         len(st.session_state.added_locations_dict['lat_longs'])
    curr_multiselected = st.sidebar.multiselect(f'Places available to select: '
                                                f'{num_able_to_select}',
                                                st.session_state.added_locations_dict["addresses"] +
                                                st.session_state.added_locations_dict["place_names"] +
                                                st.session_state.added_locations_dict['lat_longs'],
                                                default=st.session_state.active_selections)

    # Uses this temporary variable to compare and see if any selections have changed. If so, it updates the
    # session_state variable and calls the add_place_to_active function to update the current active selections.
    # Uses a temp variable and if statement so that it doesn't constantly rerun (and do the other stuff too I think :)
    if curr_multiselected != st.session_state.active_selections:
        st.session_state.active_selections = curr_multiselected
        add_place_to_active_selections()
    if st.sidebar.button('Clear Places'):
        st.session_state.added_locations_dict = {'addresses': [], 'place_names': [], 'lat_longs': []}
        st.session_state.active_selections = []
        st.session_state.active_places_df_dict = {}
        st.experimental_rerun()
