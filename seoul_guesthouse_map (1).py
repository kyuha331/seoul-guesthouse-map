
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pyproj import Transformer
import json

st.set_page_config(page_title="서울 외국인 도시민박업 지도", layout="wide")
st.title("📍 서울 외국인 도시민박업 위치 시각화")

# JSON 자동 로딩 (같은 디렉토리에 있는 파일 사용)
JSON_PATH = "서울시 외국인도시민박업 인허가 정보.json"
try:
    with open(JSON_PATH, encoding="utf-8") as f:
        raw_data = json.load(f)
    df = pd.DataFrame(raw_data["DATA"])

    # 좌표 전처리
    df = df[df['x'].str.strip().astype(bool) & df['y'].str.strip().astype(bool)]
    transformer = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)
    df[['lon', 'lat']] = df.apply(lambda row: pd.Series(transformer.transform(float(row['x']), float(row['y']))), axis=1)

    # 사이드바 필터
    with st.sidebar:
        st.header("🔍 필터 옵션")
        selected_status = st.multiselect("영업 상태", options=df['trdstatenm'].unique().tolist(), default=["영업/정상"])
        selected_bdng = st.multiselect("건물 용도", options=sorted(df['bdngsrvnm'].dropna().unique()), default=[])

    df_filtered = df[df['trdstatenm'].isin(selected_status)]
    if selected_bdng:
        df_filtered = df_filtered[df_filtered['bdngsrvnm'].isin(selected_bdng)]

    # 지도 생성 및 마커 표시 (클러스터링 포함)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
    from folium.plugins import MarkerCluster
    cluster = MarkerCluster().add_to(m)

    for _, row in df_filtered.iterrows():
        popup_text = f"{row['bplcnm']}<br>{row.get('rdnwhladdr') or row.get('sitewhladdr')}"
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=row['bplcnm'],
            icon=folium.Icon(color="blue", icon="home")
        ).add_to(cluster)

    st_folium(m, width=1000, height=700)

except FileNotFoundError:
    st.error(f"JSON 파일이 '{JSON_PATH}' 경로에 없습니다. GitHub 레포에 함께 업로드되어야 합니다.")
