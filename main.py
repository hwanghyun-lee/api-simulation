
import streamlit as st    

st.title("파이썬API 시뮬레이션 프로그램")

# Folium 지도 생성
o_latitude = 37.362124	
o_longitude = 127.114468

m = folium.Map(location=[o_latitude,o_longitude], tiles="OpenStreetMap", zoom_start=13, size = 200, show = True)
folium.TileLayer('cartodbdark_matter', name= 'Dark_Screen').add_to(m)



st.write('# streamlit test-woowayouths')
st.write('## Security Issues')

    

