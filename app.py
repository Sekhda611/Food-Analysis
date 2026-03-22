import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium


APP_TITLE = 'Food Access and Analysis'

def display_map():
    #df = df[df['State'] == state]

    m =folium.Map(location = [38,-96.5], zoom_start = 5, scrollWheelZoom = False)
    return m

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)

    # Load Data
    df_main = pd.read_csv('s_master_dataset_only_common_counties.csv')

    st.write(df_main.head())
    st.write(df_main.shape)
    st.write(df_main.isna().sum())

    #Display filters and map
    state = 'Alabama'
    m = display_map()
    st_folium(m, width = 700, height = 500)

    # Display metrics



if __name__ == '__main__':
    main()

