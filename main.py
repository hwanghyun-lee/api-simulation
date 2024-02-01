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
FC_url ="https://github.com/hwanghyun-lee/api-simulation/blob/main/weight.csv"

FC = pd.read_csv(FC_url)

st.write(FC)
    

    

