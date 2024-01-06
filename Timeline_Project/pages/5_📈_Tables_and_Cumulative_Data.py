"""
For the cumulative data:
    - total time spent there
    - average duration
    - total num visits
"""



import streamlit as st
from sys import path
path.append('Timeline_Project')
from importable_file import create_sidebar


st.set_page_config(page_title="Timeline Analyzer", page_icon="🗺️", layout="centered")


if st.session_state.data_processed:
    st.write('## Data Tables')
    # In this case, place can mean an address, place name, or lat_long tuple
    # (just means the key for each key_val pair in the active_places_df_dict+
    for place, df in st.session_state.active_places_df_dict.items():
        st.write(f'Here is the table of all your visits to: {place}')
        st.dataframe(df)
    st.write('Here is the table of all of your location data in the selected time period:')

    #### MASSIVE ERROR HERE:
    # for some reason curr_place... is a streamlit delta generator ?? and not df
    print(type(st.session_state.curr_place_visits_df))
    #st.write(st.session_state.curr_place_visits_df)

    create_sidebar()
else:
    st.write('#### Upload your Google Takeout file to begin!')