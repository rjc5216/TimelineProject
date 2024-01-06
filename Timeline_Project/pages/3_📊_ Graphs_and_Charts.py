import pandas as pd
import streamlit as st
import plotly.express as px
from sys import path
path.append('Timeline_Project')
from importable_file import create_sidebar


st.set_page_config(page_title="Timeline Analyzer", page_icon="🗺️", layout="centered")
dataFrameSerialization = "legacy"


def create_scatterplot(df, x_label, y_label, title):
    fig = px.scatter(df, x=x_label, y=y_label, title=title)

    # Updates format of the dots
    fig.update_traces(marker=dict(
        line=dict(width=0.5),  # outline of the dots
        size=10,
        color='red')
    )

    # Updates format of the layout/text/grid/ticks
    fig.update_layout(
        xaxis=dict(
            linecolor='black',
            linewidth=1.5,
            tickmode='auto',
            ticklen=6,
            tickwidth=2,
            tickcolor='black',
            showgrid=True,
            gridcolor='lightgray',
            tickfont=dict(color='black', size=14),
            titlefont=dict(color='black', size=20)
        ),
        yaxis=dict(
            linecolor='black',
            linewidth=1.5,
            tickmode='auto',
            ticklen=6,
            tickwidth=2,
            tickcolor='black',
            gridcolor='lightgray',
            tickfont=dict(color='black'),
            titlefont=dict(color='black', size=20)
        ),
        titlefont=dict(color='black'),
    )
    st.plotly_chart(fig)


if st.session_state.data_processed:
    create_sidebar()

    st.write('## Location Data Visualizations')
    st.divider()
    for place, place_df in st.session_state.active_places_df_dict.items():
        st.dataframe(place_df)
        # Uses temp_df of the date of the startTimestamp and durations to create graph
        temp_df = pd.DataFrame([place_df['startTimestamp'].dt.date, pd.to_timedelta(place_df['duration']).dt.seconds]).transpose()
        create_scatterplot(temp_df, 'startTimestamp', 'duration', f'Duration vs Date for {place}')
else:
    st.write('#### Upload your Google Takeout file to begin!')
