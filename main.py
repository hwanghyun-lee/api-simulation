#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[8]:


## 1. 법정동별이 아니라 전체 배달비 >> 주문수에 따라 계산되니 주문수 옵셔널하게 넣을 수 있을지 확인하기
## 2. 후보지 ppc 에서부터 배달건 배달품질 및 비용 ( 예 ) 성남 or 분당 선택가능하도록 )
## 3. 서현동이면 서현동만 선택해서 api 돌릴수 있도록 할것
## 4. 인근 정의 : 배달건 기준 5km 반경
        

 ####################################################################################################################
 #################### 99.Library 

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
    )

    

 ####################################################################################################################
 #################### 1.CSV 파일 불러오기


    path = '/Users/hwanghyun.lee/Desktop/파이썬_권역확장'

    ### 전체 PPC 위/경도 파일 불러오기
    FC = pd.read_csv(path+'/[FC이전] 부천_231207/Bmart_231112_분당추가.csv')

    ### PPC 권역그리기용 geojson
    df_bdong = gpd.read_file(path + '/법정동_지도그리기_전달용/korea_2307.json')
    gdf_test = gpd.read_file(path+'/[FC이전] 부천_231207/특정_법정동_추출_분당_231112.geojson')

    ### 푸드, 비마트 데이터 불러오기
    data_dlvry = pd.read_csv(path+'/[FC이전] 분당_231112/푸드_분당_231022_231104.csv')
    data_dlvry2 = pd.read_csv(path+'/[FC이전] 분당_231112/B마트_분당_231022_231104.csv')
    data_dlvry3 = pd.read_csv(path+'/[FC이전] 분당_231112/B마트_성남_231022_231104.csv')


    ### '배민1/비마트 배달 데이터 가지고 오기' 에서 추출함
    data = pd.read_csv(path+'/[FC이전] 부천_231207/B마트_분당_231022_231104.csv')





 ####################################################################################################################
 #################### 2. 사이드바

    st.sidebar.title("PPC 정보입력")

    # PPC selectedbox 만들기    

    ### B마트로 시작하는 ppc 추출
    ppc = FC[FC['name'].str.startswith('B마트')]['name'].values

    st.sidebar.header("기존PPC")
    default_ppc = 'B마트 분당'  # 초기 선택값을 'B마트 분당'으로 설정
    selected_ppc = st.sidebar.selectbox('선택', ppc, index=ppc.tolist().index(default_ppc))

    ### 사이드바에서 선택한 PPC의 데이터 가져오기
    selected_ppc_data = FC[FC['name'] == selected_ppc]



    ### 선택한 PPC의 위도와 경도를 할당
    o_latitude = selected_ppc_data['latitude'].values[0]
    o_longitude = selected_ppc_data['longitude'].values[0]


    o_latitude = st.sidebar.number_input("위도 확인", min_value=-90.0, max_value=90.0, value=o_latitude, step=1e-5)
    o_longitude = st.sidebar.number_input("경도 확인", min_value=-180.0, max_value=180.0, value=o_longitude, step=1e-5)

    a_latitude = 37.362124
    a_longitude = 127.114468   

    st.sidebar.header("후보지PPC")
    a_latitude = st.sidebar.number_input("위도 입력", min_value=-90.0, max_value=90.0, value=a_latitude, step=1e-5)
    a_longitude = st.sidebar.number_input("경도 입력", min_value=-180.0, max_value=180.0, value=a_longitude, step=1e-5)












 ############################################################################################################    
 ######################## 3. folium 지도에 기존/후보지 PPC 위치 및 data marker 생성    


    st.title("파이썬API 시뮬레이션 프로그램")

    # Folium 지도 생성
    m = folium.Map(location=[o_latitude,o_longitude], tiles="OpenStreetMap", zoom_start=13, size = 200, show = True)
    folium.TileLayer('cartodbdark_matter', name= 'Dark_Screen').add_to(m)
 




    #기존PPC 마커 추가
    marker_text = selected_ppc
    marker_location = [o_latitude,o_longitude]
    folium.Marker(location=marker_location, 
                  popup=marker_text,
                  tooltip=selected_ppc,
                  icon=folium.Icon(color='green', icon='star')).add_to(m)



    #후보지PPC 마커 추가
    marker_text = "후보지PPC"
    marker_location = [a_latitude,a_longitude]
    folium.Marker(location=marker_location, 
                  popup=marker_text,
                  tooltip="후보지PPC",
                  icon=folium.Icon(color='blue', icon='star')).add_to(m)    




    ## 비마트 및 푸드 featuregroup 생성

    fg3 = folium.FeatureGroup(name = '푸드_분당')
    fg4 = folium.FeatureGroup(name = '비마트_분당')
    fg5 = folium.FeatureGroup(name = 'B마트_성남')


    m.add_child(fg3)
    m.add_child(fg4)
    m.add_child(fg5)



 ####################################################################################################################
 #################### 4. folium 지도에 데이터 찍기 및 권역 나누기




    ### 시뮬레이션 돌릴 데이터 개수 정하기
    data_Bmart4 = data
    data_Bmart4 = data_Bmart4[0:5]

    rgn3_values = data_Bmart4['rgn3_nm'].unique().tolist()

    st.sidebar.header("법정동 선택")

    ### selectbox 생성 초기값으로 첫번쨰 rgn_3
    default_value = rgn3_values[0] if rgn3_values else None
    selected_rgn3 = st.sidebar.multiselect("선택", rgn3_values, default=default_value)

    data_Bmart5 = data_Bmart4[data_Bmart4['rgn3_nm'].isin(selected_rgn3)]
    data_Bmart5 = data_Bmart5.reset_index(drop=True)  # 행 인덱스 재설정





    ### 푸드데이터 / 비마트 데이터 지도에 표시하기

    #### dlvry(푸드_분당)데이터 위경도를 노란색으로 반지름 10 표기
    for lat, long in zip(data_dlvry['dlvry_loc_pnt_lat'], data_dlvry['dlvry_loc_pnt_lon']):

        folium.Circle(location = [lat, long], radius = 10, color='yellow').add_to(fg3)


    #### dlvry(비마트_분당)데이터 위경도를 파란색으로 반지름 10 표기
    for lat, long in zip(data_Bmart5['dlvry_loc_pnt_lat'], data_Bmart5['dlvry_loc_pnt_lon']):

        folium.Circle(location = [lat, long], radius = 10, color='red').add_to(fg4)        


    #### dlvry(비마트_성남)데이터 위경도를 분홍색으로 반지름 10 표기
    for lat, long in zip(data_dlvry3['dlvry_loc_pnt_lat'], data_dlvry3['dlvry_loc_pnt_lon']):

        folium.Circle(location = [lat, long], radius = 10, color='pink').add_to(fg5)        









    ### 전체법정동 featuregroup설정
    fg = folium.FeatureGroup(name = '법정동(분당)', show = False)
    ### 지도에 추가
    m.add_child(fg)


    ### 지도에 마우스 컨택 시 위도와 경도 정보를 팝업 형태로 표시
    folium.LatLngPopup().add_to(m)

    ### fc_name을 키로 하는 FeatureGroup 사전 생성
    layer_dict = {}

    ### 다양한 색상 리스트
    color = ['blue']




    ### 각 법정동에대한 다각형을 지도에 추가
    for idx, row in gdf_test.iterrows():
        dong_name = row['EMD_KOR_NM'] ## 법정동 명
        polygon_wkt = row['geometry'] ## 법정동파일에 있는 위/경도 정보

        ### 이미 해당 ppc_name에 대한 FeatureGroup이 있는지 확인
        if dong_name+'(법정동)' in layer_dict:
            layer = layer_dict[dong_name+'(법정동)']
        else:
            ### 해당 fc_name에 대한 FeatureGroup가 없으면 새로 생성
            layer = folium.FeatureGroup(name=dong_name+'(법정동)')
            layer_dict[dong_name+'(법정동)'] = layer

    ### geojson data를 지도에 추가    
        t1 = folium.GeoJson(polygon_wkt, 
                           style_function=lambda feature, color=color: {
                               'fillColor': color, #다각형 내부 색상
                               'color': color, #다각형 테두리
                               'weight': 3, #테두리 두깨
                               'fillOpacity': 0.1, #내부 채우는 투명도
                               'opacity': 1  # 테두리 투명도 조절
                           },
                            tooltip=f'법정동 이름: {dong_name}') # 마우스 갖다댔을 때 법정동이름 표시
        t1.add_to(layer)

    ### FeatureGroup을 맵에 추가
    for layer in layer_dict.values():
        layer.add_to(m)
        layer.add_to(fg)

    ### collapsed=False: 항상 펼쳐진 상태로 표시
    folium.LayerControl(collapsed=False,autoZIndex=False).add_to(m)    

    ### 지도 저장 및 보기
    draw = plug.Draw(export=True)
    draw.add_to(m)

    folium_static(m,width=1200, height=800)





     ####################################################################################################################   
    

        

if __name__ == "__main__":
    main()



    
    
    
    

