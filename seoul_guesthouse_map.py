
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pyproj import Transformer
import json

st.set_page_config(page_title="서울 외국인 도시민박업 지도", layout="wide")
st.title("📍 서울 외국인 도시민박업 위치 시각화")

# JSON 파일 업로드
uploaded_file = st.file_uploader("✅ JSON 파일을 업로드하세요", type=["json"])
if uploaded_file:
    raw_data = json.load(uploaded_file)
    data = raw_data['DATA']
    df = pd.DataFrame(data)

    # 좌표 유효성 필터링
    df = df[df['x'].str.strip().astype(bool) & df['y'].str.strip().astype(bool)]

    # 좌표 변환 (EPSG:5179 → WGS84)
    transformer = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)
    df[['lon', 'lat']] = df.apply(lambda row: pd.Series(transformer.transform(float(row['x']), float(row['y']))), axis=1)

    # 필터 옵션
    with st.sidebar:
        st.header("🔍 필터 옵션")
        selected_status = st.multiselect("영업 상태", options=df['trdstatenm'].unique().tolist(), default=["영업/정상"])
        selected_bdng = st.multiselect("건물 용도", options=sorted(df['bdngsrvnm'].dropna().unique()), default=[])

    # 필터 적용
    df_filtered = df[df['trdstatenm'].isin(selected_status)]
    if selected_bdng:
        df_filtered = df_filtered[df_filtered['bdngsrvnm'].isin(selected_bdng)]

    # 지도 생성
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
    for _, row in df_filtered.iterrows():
        popup_text = f"{row['bplcnm']}<br>{row.get('rdnwhladdr') or row.get('sitewhladdr')}"
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=row['bplcnm']
        ).add_to(m)

    st_folium(m, width=1000, height=700)
else:
    st.info("왼쪽 사이드바에서 JSON 파일을 업로드하면 지도가 표시됩니다.")
