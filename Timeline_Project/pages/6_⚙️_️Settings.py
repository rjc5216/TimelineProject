"""
Settings page, to allow the user to configure various settings of the project.
"""
import streamlit as st

st.set_page_config(page_title="Timeline Analyzer", page_icon="🗺️", layout="centered")

st.write('### Display Settings')
st.divider()
st.write('##### Map Marker Color:')
color_name_options = ['lightgray', 'pink', 'darkred', 'red', 'lightblue', 'darkblue', 'darkpurple', 'green', 'blue',
                      'lightgreen', 'lightred', 'gray', 'cadetblue', 'orange', 'purple', 'darkgreen', 'black', 'beige',
                      'white']
color = st.selectbox(label='', options=['Select Color'] + color_name_options)
if color != st.session_state.settings_dict['map_marker_color']:
    st.session_state.settings_dict['map_marker_color'] = color
