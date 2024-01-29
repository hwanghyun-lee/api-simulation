
import geopandas as gpd
import streamlit as st
import pandas as pd
import json
import folium
import folium.plugins as plug
import random
import numpy as np

import matplotlib.pyplot as plt
import urllib3
import requests
import time
import datetime as dt
import math


from streamlit_folium import folium_static
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic
from sklearn.datasets import load_iris




def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

    


    


def main():


#################### 0.경로지정 및 세팅




    # Set page configuration
    st.set_page_config(
        page_title="woowayouths",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",  # "wide" or "centered"
        initial_sidebar_state="auto"  # "auto", "expanded", "collapsed"
    view =[100, 500, 200]
    st.write('# streamlit test')
    st.write('## woowayouths')

    )
        

if __name__ == "__main__":
    main()


    

