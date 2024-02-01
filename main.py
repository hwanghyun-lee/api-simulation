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
from folium import plugins





# Set page configuration
st.set_page_config(
    page_title="woowayouths",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",  # "wide" or "centered"
    initial_sidebar_state="auto"  # "auto", "expanded", "collapsed"
)



####################################################################################################################
#################### 1.CSV 파일 불러오기



### 전체 PPC 위/경도 파일 불러오기
FC_url ="https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/Bmart_231112.csv"


### PPC 권역그리기용 geojson
gdf_test_url = "https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/bddong_geojson.geojson"

data_dlvry_url = "https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/food.csv"
data_dlvry2_url = "https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/bmart_boondang.csv"
data_dlvry3_url = "https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/bmart_sungsam.csv"
data_url = "https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/bmart_boondang.csv"






FC = pd.read_csv(FC_url)
gdf_test = gpd.read_file(gdf_test_url)

data_dlvry = pd.read_csv(data_dlvry_url)
data_dlvry2 = pd.read_csv(data_dlvry2_url)
data_dlvry3 = pd.read_csv(data_dlvry3_url)
data = pd.read_csv(data_url)


st.write(FC)
    

    

