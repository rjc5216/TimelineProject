# cd C:\Users\rjc52\PycharmProjects\TimelineProject\Timeline_Project
# streamlit run 📁_Upload_Files.py

"""
This is the initial page of the Timeline Project app, where users can upload the Google Takeout zip file and
have all the JSON files for each month processed.

Todo:

-- optimize the bad algorithm in add_selection() in importable_file that's rerunning get_place_df() for every place
   every time a new place is added - need a more efficient way
-- fix bug where, when you add a marker from the map, it's not initially showing up on page 3
------- fix the stupid Duration error and get the y axis data working!!!!!!!!!!

------------------ Marker CLUSTERS!!!!!!!
------------- github!!!

Future ideas:
 -- Allow the user to combine multiple similar place names into the same object and aggregate data
    (e.g. White Pass, White Pass Village Inn, White Pass Resort.... - want to display cumulative data from all of them)


---- restrict date range!!!!!???!?!??!?!?!?

-- a clear button for file? just might be nice to reset to original state before anything is uploaded

- see if, since processing doesn't seem to be taking too long, it would be better to go ahead and convert the timezones
  directly during processing to avoid the delay when users select specific places


Done:
-- figure out why there are a bunch of different prana lanes but only the main one appears in the main df????
SOLVED!! Had to standardize/clean address strings to account for things like Lane = Ln, remove extended zip codes, ...
-- make lat/longs a tuple!
--- figure out what's wrong with the timestamp timezones (in 2018, dec is off by 5 hours
    but aug is by 4 - should be 4 from UTC???)
SOLVED!! The issue was daylight savings time drifting things by an hour - UTC is actually 5 off normally
-- OPTIMIZE ADJUST TIMEZONE --- creating TimeZoneFinder object takes foreverrrr, optimize that somehow
"""
import numpy

import streamlit as st
import zipfile
import pandas as pd
import os
import re
import json
import time
from dateutil import parser
from pytz import timezone
from timezonefinder import TimezoneFinder


def set_session_state():
    """Initializes the global session state variables if they have not already been."""
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
        st.session_state.data_processed = False
    # Contains all 3 types of locations added from the second page (not multiselect)
    if 'added_locations_dict' not in st.session_state:
        st.session_state.added_locations_dict = {'addresses': [], 'place_names': [], 'lat_longs': []}
    # Active_selections is the currently selected places in the multiselect
    if 'active_selections' not in st.session_state:
        st.session_state.active_selections = []
    # This is the master dict of all currently selected places and their corresponding dataframes
    if 'active_places_df_dict' not in st.session_state:
        st.session_state.active_places_df_dict = {}


def standardize_address(address):
    """
    This function cleans and standardizes the addresses acquired from the JSON files.
    It ensures that street names with abbreviations are all counted together (Lane = Ln.), and that
    all zip codes are formatted the same (without the 4-digit extension) to maximize accuracy when collecting all
    the visits to a single place.
    """
    # Each value is a list in case you want to add other identifiers to replace with each non-abbreviated word
    # Be careful though - don't accidentally replace something (ex. if you add St to the Street list, it will replace
    # United States with United Streetates)
    standardized_addresses = {
        'Street,': ['St,'],
        'Lane,': ['Ln,'],
        'Avenue,': ['Ave,'],
        'Road,': ['Rd,'],
        'Court,': ['Ct,'],
        'USA': ['United States'],
        ', FL': [', Florida']
    }

    for key, variation_list in standardized_addresses.items():
        for variation in variation_list:
            if variation in address:
                address = address.replace(variation, key)

    # \d means a digit, {n} means the number of them, and (?=,) means to identify strings with a comma directly
    # afterwards but not grab the comma itself (there was one instance where if I didn't count the comma, it incorrectly
    # identified a street number as an extended zip code - checking for it just for completeness and accuracy)
    reg_exp = r'(\d{5}-\d{4}(?=,))'
    matches = re.findall(reg_exp, address)
    # I tested and ensured that the length of matches is only ever 0 or 1, so I can just access the first element here
    # to correctly replace the extended zip code
    if matches:
        address = address.replace(matches[0], matches[0][:-5])

    return address


def main():
    st.set_page_config(page_title="Timeline Analyzer", page_icon="🗺️", layout="centered")
    set_session_state()
    st.write('# 🗺️📌')
    st.write('# Welcome to the Google Maps Timeline Analyzer!')
    st.write('To get started, click on the following link to download your Google Takeout location history data:\n'
             'https://takeout.google.com/settings/takeout/custom/location_history?pli=1')
    st.write('Once you\'ve downloaded your files (it may take several minutes), upload the entire zipped folder here:')

    file = st.file_uploader(' ', type=['zip'])
    if file is not None:
        st.session_state.current_file = file
    if st.session_state.current_file is not None:
        # Only processes data if it hasn't been already
        # (avoids processing the new Nonetype file when the page reloads and file_uploader resets)
        if not st.session_state.data_processed:
            location_history_folder = extract_data(file)
            st.session_state.place_visits_df = process_data(location_history_folder)
            st.session_state.unique_lists_dict = get_unique_lists_dict(st.session_state.place_visits_df)
            st.session_state.data_processed = True
            st.write('✅ File Processed Successfully!')
        st.write('Current processed file: ', st.session_state.current_file.name)


def extract_data(file):
    """Extracts the zip takeout file to the local Timeline_Project directory, and returns the path to the folder."""
    zip_folder = f'C:/Users/rjc52/Downloads/{file.name}'
    extract_to = 'C:/Users/rjc52/PycharmProjects/Streamlit_Stuff/Timeline_Project'

    with zipfile.ZipFile(zip_folder, 'r') as zip_file:
        zip_file.extractall(extract_to)

    return f'{extract_to}/Takeout/Location History/Semantic Location History'


@st.cache_data
def process_data(location_history_folder):
    """Processes data from all JSON files and creates and caches the main place_visits dataframe."""
    # Adds all the data from each file to a list then creates a df with it afterwards.
    place_visits_list = []
    start = time.time()
    # Creates just on tz_object and passes to adjust_timezone() to save a ton of time
    tz_object = TimezoneFinder()
    # Nested loop to access every month file within every year folder
    for year_folder_name in os.listdir(location_history_folder):
        year_folder = os.path.join(location_history_folder, year_folder_name)
        for month_file_name in os.listdir(year_folder):
            month_file = os.path.join(year_folder, month_file_name)
            # Opens each file and processes JSON data
            with open(month_file, 'r') as current_file:
                json_data = json.load(current_file)

                # Each JSON file from the Google Takeout is a dict with 1 key - timelineObjects. The val is list of
                # dictionaries, where each one has 1 key that is either an activitySegment or a placeVisit. The
                # following code only gathers the necessary data from the inner dictionaries that are placeVisits.
                for dictionary in json_data['timelineObjects']:
                    if 'placeVisit' in dictionary.keys():
                        place_visit_dict = dictionary['placeVisit']

                        # Sets the name, address, and lat/long to None if missing (could make this into a function)
                        if 'name' in place_visit_dict['location']:
                            place_name = place_visit_dict['location']['name']
                        else:
                            place_name = None
                        if 'address' in place_visit_dict['location']:
                            # Standardizes the addresses if there is one
                            address = place_visit_dict['location']['address']
                            address = standardize_address(address)
                        else:
                            address = None
                        if 'latitudeE7' in place_visit_dict['location'] and 'longitudeE7' in place_visit_dict['location']:
                            # Gets the lat/long from the dict and converts them from E7 to standard form
                            lat, long = place_visit_dict['location']['latitudeE7'] / 10 ** 7, \
                                        place_visit_dict['location']['longitudeE7'] / 10 ** 7
                        else:
                            lat, long = None, None

                        # Creates datetime objects with the start/end times so the duration can be calculated
                        start_time_object = adjust_timezone(parser.parse(place_visit_dict['duration']['startTimestamp']), lat, long, tz_object)
                        end_time_object = adjust_timezone(parser.parse(place_visit_dict['duration']['endTimestamp']), lat, long, tz_object)
                        duration = end_time_object - start_time_object
                        new_row = [
                            lat, long, address, place_name, start_time_object, end_time_object, str(duration)
                        ]
                        place_visits_list.append(new_row)
    place_visits_df = pd.DataFrame(place_visits_list, columns=['latitudeE7', 'longitudeE7', 'address', 'name',
                                                               'startTimestamp', 'endTimestamp', 'duration'])
    end_time = time.time()
    # Sorts by the datetime of the start time (messes up the order of the indices which isn't too important - just don't
    # try to access the DF by .loc for anything sequential
    place_visits_df = place_visits_df.sort_values(by=['startTimestamp'])
    st.write(f'time: {end_time-start:.3f}\ntotal visits: {len(place_visits_df)}')
    return place_visits_df


def adjust_timezone(dt_object, lat, long, tz_object):
    """
    Adjusts the given datetime object into an accurate and readable format, converting to 12 hour format and accounting
    for timezones and daylight savings time.
    """
    # Only changes the timezone if there is location data to work with (lat and long are not None)
    if lat and long:
        # Initializes timezone object with TimeZoneFinder module and
        # gets the timezone string for the given lat/long (eg. 'America/Los Angeles')
        tz_str = tz_object.timezone_at(lat=lat, lng=long)

        # Uses the string with pytz and dateutil's astimezone() method to convert the time, which automatically
        # accounts for DST
        tz = timezone(tz_str)
        dt_object = dt_object.astimezone(tz)
    return dt_object


@st.cache_data
def get_unique_lists_dict(place_visits_df):
    """
    Returns and caches dict containing keys latitudes, longitudes, addresses, names, and durations corresponding to
    a list of all those unique attributes (removes duplicates).
    """
    start = time.time()
    unique_lists_dict = {'lat_longs': [], 'addresses': [], 'names': [], 'durations': []}
    for i in range(len(place_visits_df)):
        # Adds a tuple of (lat, long) to the lat_longs list, ensuring no NaNs are added
        lat_long_tuple = (place_visits_df.loc[i]['latitudeE7'], place_visits_df.loc[i]['longitudeE7'])
        if not pd.isna(lat_long_tuple[0]):
            unique_lists_dict['lat_longs'].append(lat_long_tuple)
        unique_lists_dict['addresses'].append(place_visits_df.loc[i]['address'])
        unique_lists_dict['names'].append(place_visits_df.loc[i]['name'])
        unique_lists_dict['durations'].append(place_visits_df.loc[i]['duration'])
    # Converts the val (a list of all the lats/longs...) to a set to remove duplicates, then converts back to a list
    # to make other things like concatenation and ordering easier
    unique_lists_dict = {key: list(set(val)) for key, val in unique_lists_dict.items()}
    st.write(unique_lists_dict['lat_longs'])
    # st.write(f'unique time: {time.time() - start: .3f}')
    # st.write(unique_lists_dict)
    return unique_lists_dict


if __name__ == '__main__':
    main()
