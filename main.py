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
from streamlit_folium import folium_static
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic





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


    
####################################################################################################################
#################### 1.CSV 파일 불러오기



    ### 전체 PPC 위/경도 파일 불러오기
    FC_url ="https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/Bmart_231112.csv"
    
    
    ### PPC 권역그리기용 geojson
    gdf_test_url = "https://raw.githubusercontent.com/hwanghyun-lee/api-simulation/main/bbdong_bundang.geojson"
    
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


    o_latitude = st.sidebar.number_input("위도 확인", min_value=-90.0, max_value=90.0, value=o_latitude, step=1e-5, format="%.5f")
    o_longitude = st.sidebar.number_input("경도 확인", min_value=-180.0, max_value=180.0, value=o_longitude, step=1e-5, format="%.5f")

    a_latitude = 37.362124
    a_longitude = 127.114468   

    st.sidebar.header("후보지PPC")
    a_latitude = st.sidebar.number_input("위도 입력", min_value=-90.0, max_value=90.0, value=a_latitude, step=1e-5, format="%.5f")
    a_longitude = st.sidebar.number_input("경도 입력", min_value=-180.0, max_value=180.0, value=a_longitude, step=1e-5, format="%.5f")

    







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

    fg3 = folium.FeatureGroup(name = '푸드_분당', show = False)
    fg4 = folium.FeatureGroup(name = selected_ppc, show = True)
    fg5 = folium.FeatureGroup(name = 'B마트_성남', show = False)


    m.add_child(fg3)
    m.add_child(fg4)
    m.add_child(fg5)



 ####################################################################################################################
 #################### 4. folium 지도에 데이터 찍기 및 권역 나누기




    ### 시뮬레이션 돌릴 데이터 개수 정하기
    data_Bmart3 = data
#    data_Bmart4 = data_Bmart3
    data_Bmart4 = data_Bmart3[0:10]

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
    fg = folium.FeatureGroup(name = '법정동(분당)', show = True)
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
    

    st.sidebar.title(" ")
    st.sidebar.title("일부권역 조회")
#    st.sidebar.header("일부권역 조회시")
    # 텍스트 입력 받기
    geojson_text = st.sidebar.text_area("다각형 좌표 데이터 입력")






 ############################################################################################################    
 ############################## 5. 아이나비 API 연결




    api_key = '6a86251539dc1e3f9a47a30f019475c9f4ffaf00' ## 아이나비 API

    def get_distance(lon1, lat1, lon2, lat2):
        url = "https://wb-maps.inavi.com/maps/v3.0/appkeys/{appkey}/route-normal?option=baemin_rider&coordType=wgs84&startX={startX}&startY={startY}&endX={endX}&endY={endY}&useStartDirection=true&epSearch=true"

        url = url.replace("{appkey}", api_key)
        url = url.replace("{startX}", str(lon1))
        url = url.replace("{startY}", str(lat1))
        url = url.replace("{endX}", str(lon2))
        url = url.replace("{endY}", str(lat2))
        

            
        myInavi = requests.get(url= url, verify = False).json()   
        return myInavi['route']['data']['distance'], myInavi['route']['data']['spend_time']



 ############################################################################################################  
    
 ############################### 6. Polygon 데이터 배달품질 계산   

    ###### 실행버튼 생성 및 polygon 내부 데이터 추출
    if st.sidebar.button("Run API (Polygon region)"):

        if geojson_text:
            


            # GeoJSON 텍스트를 JSON으로 파싱
            geojson_data = json.loads(geojson_text)

            # 다각형의 좌표 정보 추출 (첫 번째 Polygon만 고려)
            polygon_coordinates = geojson_data['geometry']['coordinates'][0]
            polygon2 = Polygon(polygon_coordinates)

            data_Bmart6 = data_Bmart5
            data_Bmart6['inside'] = data_Bmart6.apply(lambda x: polygon2.contains(Point(x['dlvry_loc_pnt_lon'], x['dlvry_loc_pnt_lat'])), axis=1)  
            data_Bmart6 = data_Bmart6[data_Bmart6['inside']==True]
            data_Bmart6 = data_Bmart6.reset_index(drop=True)  # 행 인덱스 재설정

        else:
            st.warning("다각형 좌표 데이터를 먼저 입력하세요.")

            
            
       ###### 후보지 배달품질 및 비용 계산
        start = time.time()
        count = 0 

        diss = []
        hand_over_time = []


        FC_lat = a_latitude
        FC_lon = a_longitude

        candidate_distance = "후보지 배달거리"
        candidate_time = "후보지 전달시간(아이나비)"



        for i in range(data_Bmart6.shape[0]):

            ## 배달데이터의 위경도 
            lon2 = data_Bmart6["dlvry_loc_pnt_lon"][i]
            lat2 = data_Bmart6["dlvry_loc_pnt_lat"][i]


            ## PPC에서 배달지까지의 위/경도 거리, 시간 
            distance_result, time_result = get_distance(FC_lon, FC_lat, lon2, lat2)
            time_result_60 =time_result/60


            ##DF에 결과 쌓기
            diss.append(distance_result)
            hand_over_time.append(time_result_60)

            data_Bmart6[candidate_distance] = pd.DataFrame(diss)
            data_Bmart6[candidate_time] = pd.DataFrame(hand_over_time)


            count += 1

        end = time.time()


        ### 아이나비 사용내역
        st.sidebar.header("API 사용내역")
        st.sidebar.write(f"API 소요시간 : {end - start:.1f} sec")
        st.sidebar.write(f"API 사용량 : {count:.1f} case")
        
        
        
        


      ################################## 전체 배달데이터 활용 기존ppc 배달품질 계산
        data_Bmart6['Now_consign_dates'] = ((pd.to_datetime(data_Bmart6['consign_date'])  - pd.to_datetime(data_Bmart6['reg_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart6['Now_arrived_shop_dates'] = ((pd.to_datetime(data_Bmart6['arrived_shop_date'])  - pd.to_datetime(data_Bmart6['consign_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart6['Now_pick_up_dates'] = ((pd.to_datetime(data_Bmart6['pick_up_date'])  - pd.to_datetime(data_Bmart6['arrived_shop_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart6['Now_hand_over_times'] = ((pd.to_datetime(data_Bmart6['hand_over_date'])  - pd.to_datetime(data_Bmart6['pick_up_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart6['Now_dlvry_time'] = data_Bmart6['Now_consign_dates'] + data_Bmart6['Now_arrived_shop_dates'] + data_Bmart6['Now_pick_up_dates'] + data_Bmart6['Now_hand_over_times']




        ############################### 7-2) 선택한 법정동 거리기반 기본배달비 계산


        candidate_distance = "후보지 배달거리"
        candidate_fee = "후보지 배달비"

        #### 거리기반 new_fee 계산
        data_Bmart6[candidate_fee] = 0

        data_Bmart6.loc[(data_Bmart6[candidate_distance] >= 0) & (data_Bmart6[candidate_distance] < 675),candidate_fee]  = 3000
        data_Bmart6.loc[(data_Bmart6[candidate_distance] >= 675) & (data_Bmart6[candidate_distance] < 1900),candidate_fee]  = 3500
        data_Bmart6.loc[(data_Bmart6[candidate_distance] >= 1900),candidate_fee]  = 3500 + ((data_Bmart6[candidate_distance] - 1900) / 100).apply(np.ceil) * 80  

        




        ############################### 7-3) 선택한 법정동 거리기반 배달품질(전달시간, 배달시간) 계산


        candidate_distance = "후보지 배달거리"
        candidate_fee = "후보지 배달비"
        candidate_hand_over_times = "후보지 전달시간"
        candidate_dlvry_time = "후보지 배달시간"

        ### 전달시간 계산 (변화된 거리에 비례)
        data_Bmart6[candidate_hand_over_times] = (data_Bmart6[candidate_distance] * data_Bmart6['Now_hand_over_times'] / data_Bmart6['actual_dlvry_distance']).round(decimals=2)
        ### 배달시간 계산 (변화된 전달시간 반영)
        data_Bmart6[candidate_dlvry_time] = data_Bmart6['Now_consign_dates'] + data_Bmart6['Now_arrived_shop_dates'] + data_Bmart6['Now_pick_up_dates'] + data_Bmart6[candidate_hand_over_times]

        ### 컬럼명 변경
        data_dlvry_rename = data_Bmart6.rename(columns = {'names': 'PPC','rgn3_nm': "법정동",'base_fee': "기본배달비(원)" ,'rider_dlvry_fee':'건당배달비(원)', 'actual_dlvry_distance': "배달거리(m)",'Now_hand_over_times': "전달시간(분)", 'Now_dlvry_time': "배달시간(분)"})




        
        
        
        
        
        

        ############################### 기존ppc 품질 및 비용 평균값 계산
        selected_columns_orgin = ['PPC','법정동','기본배달비(원)','건당배달비(원)','배달거리(m)',"전달시간(분)","배달시간(분)"]
        data_Bmart_origin_filter = data_dlvry_rename[selected_columns_orgin]
        data_Bmart_origin = data_Bmart_origin_filter.groupby(['PPC','법정동']).mean()[['기본배달비(원)',"전달시간(분)","배달시간(분)",'배달거리(m)']].round(decimals=2)

        



        

        ############################### 후보지ppc 품질 및 비용 평균값 계산
        selected_columns_candidate = ['PPC','법정동','후보지 배달비','후보지 배달거리',"후보지 전달시간(아이나비)", "후보지 전달시간","후보지 배달시간"]
        data_Bmart_candidate1_filter = data_dlvry_rename[selected_columns_candidate]

        #### 컬럼명 통일
        data_Bmart_candidate1_filter = data_Bmart_candidate1_filter.rename(columns={'후보지 배달비': '기본배달비(원)', '후보지 전달시간' : '전달시간(분)','후보지 배달시간' : '배달시간(분)','후보지 배달거리' : '배달거리(m)', "후보지 전달시간(아이나비)" : '전달시간(아이나비)' })

        data_Bmart_candidate1 = data_Bmart_candidate1_filter.groupby(['PPC','법정동']).mean()[['기본배달비(원)', "전달시간(분)","배달시간(분)",'배달거리(m)']].round(decimals=2)

        
        
        
        
       

        
        
        
        

        st.subheader("기존PPC) Polygon 내부 법정동별 배달품질 및 비용")

        st.table(data_Bmart_origin.style
             .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'td', 'props': [('text-align', 'center')]},# 모든 셀 중앙 정렬
                                {'selector': 'tr', 'props': [('height', '30px')]}]) # 행 높이 조절
        .format({"기본배달비(원)": "{:.0f}", "배달거리(m)": "{:.0f}", "전달시간(분)": "{:.1f}", "배달시간(분)": "{:.1f}"}))

        
    
    
        st.subheader("후보지PPC) Polygon 내부 법정동별 배달품질 및 비용")


        st.table(data_Bmart_candidate1.style
             .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'td', 'props': [('text-align', 'center')]},
                                {'selector': 'tr', 'props': [('height', '30px')]}])
        .format({"기본배달비(원)": "{:.0f}", "배달거리(m)": "{:.0f}", "전달시간(분)": "{:.1f}", "배달시간(분)": "{:.1f}"}))

    
    
    
    
    
    
    
    
    
############################################################################################################    
############################## 7.전체권역 배달품질 계산

#   st.sidebar.header("전체권역 조회시")
    st.sidebar.title(" ")
    st.sidebar.title("전체권역 조회")
    ### 실행버튼 생성
    if st.sidebar.button("Run API (Overall region) "):

        start = time.time()
        count = 0 

        diss = []
        hand_over_time = []


        FC_lat = a_latitude
        FC_lon = a_longitude

        candidate_distance = "후보지 배달거리"
        candidate_time = "후보지 전달시간(아이나비)"



        for i in range(data_Bmart5.shape[0]):

            ## 배달데이터의 위경도 
            lon2 = data_Bmart5["dlvry_loc_pnt_lon"][i]
            lat2 = data_Bmart5["dlvry_loc_pnt_lat"][i]


            ## PPC에서 배달지까지의 위/경도 거리, 시간 
            distance_result, time_result = get_distance(FC_lon, FC_lat, lon2, lat2)
            time_result_60 =time_result/60


            ##DF에 결과 쌓기
            diss.append(distance_result)
            hand_over_time.append(time_result_60)

            data_Bmart5[candidate_distance] = pd.DataFrame(diss)
            data_Bmart5[candidate_time] = pd.DataFrame(hand_over_time)


            count += 1

        end = time.time()


        ### 아이나비 사용내역
        st.sidebar.header("API 사용내역")
        st.sidebar.write(f"API 소요시간 : {end - start:.1f} sec")
        st.sidebar.write(f"API 사용량 : {count:.1f} case")





     ############################################################################################################        
     ############################## 7.기존ppc / 후보지Ppc 배달품질 계산


        ################################## 7-1) 선택한 법정동 배달데이터 활용 기존ppc 배달품질 계산
        data_Bmart5['Now_consign_dates'] = ((pd.to_datetime(data_Bmart5['consign_date'])  - pd.to_datetime(data_Bmart5['reg_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart5['Now_arrived_shop_dates'] = ((pd.to_datetime(data_Bmart5['arrived_shop_date'])  - pd.to_datetime(data_Bmart5['consign_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart5['Now_pick_up_dates'] = ((pd.to_datetime(data_Bmart5['pick_up_date'])  - pd.to_datetime(data_Bmart5['arrived_shop_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart5['Now_hand_over_times'] = ((pd.to_datetime(data_Bmart5['hand_over_date'])  - pd.to_datetime(data_Bmart5['pick_up_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart5['Now_dlvry_time'] = data_Bmart5['Now_consign_dates'] + data_Bmart5['Now_arrived_shop_dates'] + data_Bmart5['Now_pick_up_dates'] + data_Bmart5['Now_hand_over_times']


    



        ############################### 7-2) 선택한 법정동 거리기반 기본배달비 계산


        candidate_distance = "후보지 배달거리"
        candidate_fee = "후보지 배달비"

        #### 거리기반 new_fee 계산
        data_Bmart5[candidate_fee] = 0

        data_Bmart5.loc[(data_Bmart5[candidate_distance] >= 0) & (data_Bmart5[candidate_distance] < 675),candidate_fee]  = 3000
        data_Bmart5.loc[(data_Bmart5[candidate_distance] >= 675) & (data_Bmart5[candidate_distance] < 1900),candidate_fee]  = 3500
        data_Bmart5.loc[(data_Bmart5[candidate_distance] >= 1900),candidate_fee]  = 3500 + ((data_Bmart5[candidate_distance] - 1900) / 100).apply(np.ceil) * 80  

        




        ############################### 7-3) 선택한 법정동 거리기반 배달품질(전달시간, 배달시간) 계산


        candidate_distance = "후보지 배달거리"
        candidate_fee = "후보지 배달비"
        candidate_hand_over_times = "후보지 전달시간"
        candidate_dlvry_time = "후보지 배달시간"

        ### 전달시간 계산 (변화된 거리에 비례)
        data_Bmart5[candidate_hand_over_times] = (data_Bmart5[candidate_distance] * data_Bmart5['Now_hand_over_times'] / data_Bmart5['actual_dlvry_distance']).round(decimals=2)
        ### 배달시간 계산 (변화된 전달시간 반영)
        data_Bmart5[candidate_dlvry_time] = data_Bmart5['Now_consign_dates'] + data_Bmart5['Now_arrived_shop_dates'] + data_Bmart5['Now_pick_up_dates'] + data_Bmart5[candidate_hand_over_times]

        ### 컬럼명 변경
        data_dlvry_rename = data_Bmart5.rename(columns = {'names': 'PPC','rgn3_nm': "법정동",'base_fee': "기본배달비(원)" ,'rider_dlvry_fee':'건당배달비(원)', 'actual_dlvry_distance': "배달거리(m)",'Now_hand_over_times': "전달시간(분)", 'Now_dlvry_time': "배달시간(분)"})


        ############################### 7-4) 선택한 기존ppc 품질 및 비용 평균값 계산
        selected_columns_orgin = ['PPC','법정동','기본배달비(원)','건당배달비(원)','배달거리(m)',"전달시간(분)","배달시간(분)"]
        data_Bmart_origin_filter = data_dlvry_rename[selected_columns_orgin]
        data_Bmart_origin = data_Bmart_origin_filter.groupby(['PPC','법정동']).mean()[['기본배달비(원)',"전달시간(분)","배달시간(분)",'배달거리(m)']].round(decimals=2)

        



        

        ############################### 7-5) 후보지ppc 품질 및 비용 평균값 계산
        selected_columns_candidate = ['PPC','법정동','후보지 배달비','후보지 배달거리',"후보지 전달시간(아이나비)", "후보지 전달시간","후보지 배달시간"]
        data_Bmart_candidate1_filter = data_dlvry_rename[selected_columns_candidate]

        #### 컬럼명 통일
        data_Bmart_candidate1_filter = data_Bmart_candidate1_filter.rename(columns={'후보지 배달비': '기본배달비(원)', '후보지 전달시간' : '전달시간(분)','후보지 배달시간' : '배달시간(분)','후보지 배달거리' : '배달거리(m)', "후보지 전달시간(아이나비)" : '전달시간(아이나비)' })

        data_Bmart_candidate1 = data_Bmart_candidate1_filter.groupby(['PPC','법정동']).mean()[['기본배달비(원)', "전달시간(분)","배달시간(분)",'배달거리(m)']].round(decimals=2)

        


         ############################## 7-6 기존PPC(전체데이터) 배달품질 계산       
        
        
      ################################## 전체 배달데이터 활용 기존ppc 배달품질 계산
        data_Bmart3['Now_consign_dates'] = ((pd.to_datetime(data_Bmart3['consign_date'])  - pd.to_datetime(data_Bmart3['reg_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart3['Now_arrived_shop_dates'] = ((pd.to_datetime(data_Bmart3['arrived_shop_date'])  - pd.to_datetime(data_Bmart3['consign_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart3['Now_pick_up_dates'] = ((pd.to_datetime(data_Bmart3['pick_up_date'])  - pd.to_datetime(data_Bmart3['arrived_shop_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart3['Now_hand_over_times'] = ((pd.to_datetime(data_Bmart3['hand_over_date'])  - pd.to_datetime(data_Bmart3['pick_up_date'])).dt.total_seconds() / 60.0).round(decimals=2)

        data_Bmart3['Now_dlvry_time'] = data_Bmart3['Now_consign_dates'] + data_Bmart3['Now_arrived_shop_dates'] + data_Bmart3['Now_pick_up_dates'] + data_Bmart3['Now_hand_over_times']


        
        

        
        ############################### 전체 기존ppc 품질 및 비용 평균값 계산
        data_dlvry_rename_all = data_Bmart3.rename(columns = {'names': 'PPC','rgn3_nm': "법정동",'base_fee': "기본배달비(원)" ,'rider_dlvry_fee':'건당배달비(원)', 'actual_dlvry_distance': "배달거리(m)",'Now_hand_over_times': "전달시간(분)", 'Now_dlvry_time': "배달시간(분)"})
        
        selected_columns_orgin = ['PPC','법정동','기본배달비(원)','건당배달비(원)','배달거리(m)',"전달시간(분)","배달시간(분)"]
        data_Bmart_origin_filter_all = data_dlvry_rename_all[selected_columns_orgin]
        data_Bmart_origin_all = data_Bmart_origin_filter_all.groupby(['PPC','법정동']).mean()[['기본배달비(원)',"전달시간(분)","배달시간(분)",'배달거리(m)']].round(decimals=2)
        


        
        
        
        
        
        
        
        
        
        
        
 ############################################################################################################        
 ############################## 8.기존PPC / 후보지PPC / 기존PPC(전체data) 출력 및 서식 수정

        st.subheader("기존PPC) 선택 법정동별 배달품질 및 비용")


 
        st.table(data_Bmart_origin.style
             .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'td', 'props': [('text-align', 'center')]},# 모든 셀 중앙 정렬
                                {'selector': 'tr', 'props': [('height', '30px')]}]) # 행 높이 조절
        .format({"기본배달비(원)": "{:.0f}", "배달거리(m)": "{:.0f}", "전달시간(분)": "{:.1f}", "배달시간(분)": "{:.1f}"}))




        st.subheader("후보지PPC) 선택 법정동별 배달품질 및 비용")


        st.table(data_Bmart_candidate1.style
             .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'td', 'props': [('text-align', 'center')]},
                                {'selector': 'tr', 'props': [('height', '30px')]}])
        .format({"기본배달비(원)": "{:.0f}", "배달거리(m)": "{:.0f}", "전달시간(분)": "{:.1f}", "배달시간(분)": "{:.1f}"}))

        
        



        st.subheader("# 기존PPC 전체 법정동별 배달품질 및 비용")


 
        st.table(data_Bmart_origin_all.style
             .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]},
                                {'selector': 'td', 'props': [('text-align', 'center')]},# 모든 셀 중앙 정렬
                                {'selector': 'tr', 'props': [('height', '30px')]}]) # 행 높이 조절
        .format({"기본배달비(원)": "{:.0f}", "배달거리(m)": "{:.0f}", "전달시간(분)": "{:.1f}", "배달시간(분)": "{:.1f}"}))


        

        
            

        
    ## requirments 해결  
    ## 법정동 Geojson 따올떄 기준이 무엇인지?
    ## 서버연결시 보안이슈 어떻게 해결하는지 확인
    ## csv 데이터 링크 연결
     ####################################################################################################################   
    

        

if __name__ == "__main__":
    main()


    

