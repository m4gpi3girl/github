# import packages ------------------------------------------------------------------

# for making api request
import requests
# for api data
import json

# obv pandas
import pandas as pd
# always import this never use it but its habit at this point
import numpy as np

# for streamlit
import streamlit as st
# for folium maps in streamlit
import streamlit_folium
# to keep the map on the page 
from streamlit_folium import folium_static

# folium for maps
import folium

# data viz
import matplotlib.pyplot as plt
# data viz
import plotly
# data viz
import plotly.express as px


from modules import bulk_pc_lookup
import altair as alt
# -------------------------------------------------------------------

st.set_page_config(layout="centered")

# data import -------------------------------------------------------

fp = 'ww.xlsx'

df = pd.read_excel(fp, sheet_name="1")
df2 = pd.read_excel(fp, sheet_name="2")

# --------------------------------------------------------------------

# set up sidebar and filter ----------------------------------------------------

# selectbox
selected_space_type = st.sidebar.selectbox(
    'Space Type',
    df['Space Type'].unique()
)

# sidebar text
with st.sidebar:
    st.write("About Energy Performance Certificates (EPCs):")
    st.markdown(
        """
        - EPCs are required for all buildings (domestic and non-domestic), when constructed, sold or rented. 
        - Exemptions include buildings used as places of worship. 
        - EPCs are valid for 10 years. 
        - The EPC records how energy efficient a property is as a building, using an A+ to G rating scale where A+ is the most efficient and G is the least efficient). 
        - The certificate also lists the potential rating of the building if all the cost-effective measures are installed.
        - EPCs come with a recommendations report with retrofit measures.
        """)

# filter data based on selectbox
filtered_data = df[df['Space Type'] == selected_space_type]

#---------------------------------------------------------------------

# lookup postcodes and add to data-----------------------------------

postcodes = filtered_data['Postcode'].tolist()
op = bulk_pc_lookup(postcodes)
op_df = pd.DataFrame(op)
filtered_data = filtered_data.merge(op_df, left_on="Postcode", right_on="Charity Postcode")

# --------------------------------------------------------------------


# separate df for displaying filtered results -----------------------
filtered_data_2 = df2[df2['Space Type'] == selected_space_type]

# Title
st.title(f"Space Type: {selected_space_type}")



         
total_spaces = filtered_data["ID"].nunique()

total_with_epc = filtered_data[filtered_data['EPC'] == 1]["ID"].nunique()

total_with_dec = filtered_data[filtered_data['DEC'] == 1]["ID"].nunique()

total_no_energy = filtered_data[filtered_data['Has A Cert?'] != "Y"]['ID'].nunique()


st.write("#### Headliners")

col1,col2 = st.columns(2)




with col1:
    metric1value = total_spaces
    st.metric(label=f'Warm Spaces in Category "{selected_space_type}"', value=metric1value)

    with_data = total_spaces - total_no_energy
    st.write(f"{with_data} spaces with matches:",)

    metric2value = total_with_epc
    st.metric(label="*With EPCs*", value=metric2value)

    metric3value = total_with_dec
    st.metric(label="*With DECs*", value=metric3value)

    metric4value = total_no_energy
    st.metric(label="With No EPC or DEC Data", value=metric4value)



   
    st.write("#### Targets and Actual Emissions (Median)")

    metric9, metric8 = st.columns(2)

    with metric9:
        labels = 'Building Emissions'
        values = filtered_data_2['BUILDING_EMISSIONS'].median()
        st.metric(label=labels, value=round(values))


    with metric8:
        labels = 'Standard Emissions'
        values = filtered_data_2['STANDARD_EMISSIONS'].median()
        st.metric(label=labels, value=round(values))

    metric6, metric7 = st.columns(2)

    with metric6:
        labels = 'Target Emissions'
        values = filtered_data_2['TARGET_EMISSIONS'].median()
        st.metric(label=labels, value=round(values))

    with metric7:
        labels = 'Typical Emissions'
        values = filtered_data_2['TYPICAL_EMISSIONS'].median()
        st.metric(label=labels, value=round(values))



    metric4, metric5 = st.columns(2)

    with metric4:
        labels = 'New Build Benchmark'
        values = filtered_data_2['NEW_BUILD_BENCHMARK'].median()
        st.metric(label=labels, value=round(values))


    with metric5:
        labels = 'Existing Stock Benchmark'
        values = filtered_data_2['EXISTING_STOCK_BENCHMARK'].median()
        st.metric(label=labels, value=round(values))


with col2:

    filtered_data = filtered_data.dropna(subset=['Latitude', 'Longitude'])

    mean_lat = filtered_data['Latitude'].mean()
    mean_lon = filtered_data['Longitude'].mean()

    m = folium.Map(location=[mean_lat, mean_lon], zoom_start=6)
    
    for idx, row in filtered_data.iterrows():

        if row['Has A Cert?'] == 'Y' and row['EPC'] > 0:
            color = 'green'
        elif row['Has A Cert?'] == 'Y' and row['EPC'] == 0:
            color = 'blue'
        else:
            color = 'red'

        #color = 'green' if row['Has A Cert?'] == 'Y' else 'red'

        folium.Marker(location=[row['Latitude'], row['Longitude']], icon=folium.Icon(color=color)).add_to(m)
    
    folium_static(m, width=400, height=500)

    

    st.write("Key - Red = No Certificate, Green = Has EPC, Blue = Has DEC")

    to_count = ['A+', 'A', 'B', 'C']
    grouped_data = filtered_data_2.groupby('ID')
    number_above_c = 0

    for space_id, group in grouped_data:
        if any(rating in to_count for rating in group['ASSET_RATING_BAND_y']):
            number_above_c += 1

    length_epc = filtered_data_2['ID'].nunique()
    d_minus = length_epc - number_above_c

    st.warning(f"A total of {d_minus} EPC rated spaces are below the upcoming C minimum rating")
    
    to_count2 = ['A+', 'A', 'B']
    grouped_data2 = filtered_data_2.groupby('ID')
    number_above_c2 = 0

    for space_id, group in grouped_data2:
        if any(rating in to_count2 for rating in group['ASSET_RATING_BAND_y']):
            number_above_c2 += 1

    length_epc2 = filtered_data_2['ID'].nunique()
    c_minus = length_epc2 - number_above_c2

    st.warning(f"A total of {c_minus} EPC rated spaces are below the upcoming B minimum rating")





#--------------
    
st.write("### EPC Rating by Band")

grouped_data = filtered_data_2.groupby('ASSET_RATING_BAND_y')['ID'].count().reset_index(name='Count')

# Calculating percentage of each count out of the total count
total_count = grouped_data['Count'].sum()
grouped_data['Percentage'] = grouped_data['Count'] / total_count * 100
fig = px.bar(grouped_data, x='ASSET_RATING_BAND_y', y='Percentage', text='Count')
st.write(fig)



st.write("### Main Heating Fuel")
grouped_data = filtered_data_2.groupby('MAIN_HEATING_FUEL')['ID'].count().reset_index(name='Count')

# Calculating percentage of each count out of the total count
total_count = grouped_data['Count'].sum()
grouped_data['Percentage'] = grouped_data['Count'] / total_count * 100
fig = px.bar(grouped_data, x='MAIN_HEATING_FUEL', y='Percentage', text='Count')
st.plotly_chart(fig)


