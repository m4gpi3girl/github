import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title='Warm Welcome Spaces - Energy Efficiency', layout="wide", initial_sidebar_state="expanded")

st.title("Analysis of Energy Performance of Warm Welcome Spaces")




st.header("About this app")

st.write("This app has been developed to allow Warm Welcome spaces and partners to access the analysis and to view the data in more detail. Currently the main operational page, found in the sidebar, shows EPC data by space type. It is currently intended that this will expand to an individual space lookup, as well as some analysis of DEC certificates.")

st.success("If you have any questions about the data please get in touch at: elisha.zissman@sibgroup.org.uk")


col1, col2 = st.columns(2)
with col1:
    st.image("Warm_Welcome_Image.jpg")
with col2:
    st.image("sib.png")
