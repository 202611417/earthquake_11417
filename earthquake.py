import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import pickle

# 1. 데이터 및 모델 로드 (캐싱)
@st.cache_data
def load_data():
    return pd.read_csv('earthquake.csv')

df_new = load_data()
risk_dict = {0: '높음', 1: '낮음', 2: '중간'}

# 💡 [핵심] 버튼 클릭 상태를 저장할 세션 상태 초기화
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

# 사이드바 입력 폼
st.sidebar.header("위치 입력")
lat = st.sidebar.number_input("위도 입력:", value=37.5, format="%.4f")
lon = st.sidebar.number_input("경도 입력:", value=127.0, format="%.4f")

# 버튼을 누르면 'clicked' 상태를 True로 변경
if st.sidebar.button("위험도 확인"):
    st.session_state.clicked = True

# 💡 [핵심] 버튼을 한 번이라도 눌렀다면 화면이 새로고침되어도 계속 실행됨
if st.session_state.clicked:
    
    # 위도, 경도 입력 주변의 지진 찾기
    near_df = df_new[(df_new['위도'] >= lat-5) & (df_new['위도'] <= lat+5) & 
                     (df_new['경도'] >= lon-5) & (df_new['경도'] <= lon+5)]
    
    if near_df.empty:
        st.warning("입력한 위치의 반경 5도 이내에 지진 데이터가 없습니다.")
    else:
        # 주변 군집의 비율 계산
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = cluster_ratio.idxmax()
        
        # 결과 출력
        st.subheader(f"해당 지역의 예상 위험도: **{risk_dict[main_cluster]}**")
        
        # 지도 시각화
        m = folium.Map(location=[lat, lon], zoom_start=4)
        
        sample_size = min(1000, len(df_new))
        df_sample = df_new.sample(sample_size, random_state=42)
        colors = {0: 'red', 1: 'blue', 2: 'green'}
        
        for _, row in df_sample.iterrows():
            cluster = row['cluster']
            folium.CircleMarker(
                location=[row['위도'], row['경도']],
                radius=3, 
                color=colors.get(cluster, 'gray'),
                fill=True, 
                fill_color=colors.get(cluster, 'gray')
            ).add_to(m)
        
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='black', icon='star')
        ).add_to(m)
        
        # 💡 key 값을 지정해주면 지도가 다시 그려질 때 끊김 현상을 방지해 줍니다.
        st_folium(m, width=800, height=600, key="earthquake_map")