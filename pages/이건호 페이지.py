import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime
import json

st.set_page_config(
    page_title="스마트 VIP 경호 시스템",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .alert-box-danger {
        background-color: #4a151b;
        border: 1px solid #ff4b4b;
        padding: 15px;
        border-radius: 8px;
        color: #ff8888;
        font-weight: bold;
    }
    .alert-box-safe {
        background-color: #0f380f;
        border: 1px solid #00cc66;
        padding: 15px;
        border-radius: 8px;
        color: #88ff88;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

BASE_LAT = 37.5240
BASE_LNG = 127.0425

if "spots" not in st.session_state:
    st.session_state.spots = [
        {"name": "청담동 메인 대로변", "lat": 37.5252, "lng": 127.0435, "level": "위험", "color": "red", "type": "파파라치 밀집"},
        {"name": "주출입구 정문 로비", "lat": 37.5245, "lng": 127.0415, "level": "경고", "color": "orange", "type": "사생팬 대기 중"},
        {"name": "건물 앞 수상한 밴", "lat": 37.5230, "lng": 127.0440, "level": "주의", "color": "yellow", "type": "장기 체류 차량"}
    ]

if "logs" not in st.session_state:
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs = [
        f"[{now}] [AI 감지] 렌즈 반사 신호 자동 탐지 (청담동 대로변)",
        f"[{now}] [경호원 제보] 정문 로비 사생팬 10여 명 대기 중"
    ]

def get_distance(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2.0)**2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0)**2
    return float(r * 2 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a)))

def get_ai_report(spots, v_lat, v_lng, min_d):
    try:
        from google import genai
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ Gemini API 키가 설정되지 않았습니다. Streamlit Secrets를 확인해 주세요."
        
        client = genai.Client(api_key=api_key)
        prompt = f"""
        당신은 VIP 전문 최고 레벨 AI 경호 팀장입니다.
        현재 VIP 위치: ({v_lat}, {v_lng})
        가장 가까운 위협과의 거리: {min_d:.1f}m
        현재 감지된 위협 목록: {json.dumps(spots, ensure_ascii=False)}

        현장 경호원에게 전달할 행동 수칙 리포트를 짧고 명확하게 작성해 주세요.
        1. 현재 위협 평가
        2. 세이프 루트 회피 안내
        3. 현장 대처 지침 3가지
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI 리포트 생성 오류: {str(e)}"

st.sidebar.title("🛡️ 스마트 경호 관제")
st.sidebar.subheader("🚗 VIP 위치 조정")
vip_lat = st.sidebar.slider("VIP 위도", 37.5200, 37.5280, BASE_LAT, format="%.4f")
vip_lng = st.sidebar.slider("VIP 경도", 127.0380, 127.0460, BASE_LNG, format="%.4f")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 현장 수동 제보")
with st.sidebar.form("add_spot"):
    s_name = st.text_input("위치명", "건물 후문 골목")
    s_type = st.selectbox("유형", ["파파라치 밀집", "의심 차량 대기", "사생팬 대기 중", "드론 촬영"])
    s_level = st.selectbox("위험도", ["주의 (노란색)", "경고 (주황색)", "위험 (빨간색)"])
    s_lat = st.number_input("위도 오프셋", -0.005, 0.005, 0.001, step=0.0005, format="%.4f")
    s_lng = st.number_input("경도 오프셋", -0.005, 0.005, -0.001, step=0.0005, format="%.4f")
    
    if st.form_submit_button("위협 스팟 등록"):
        color_dict = {"주의 (노란색)": "yellow", "경고 (주황색)": "orange", "위험 (빨간색)": "red"}
        level_dict = {"주의 (노란색)": "주의", "경고 (주황색)": "경고", "위험 (빨간색)": "위험"}
        
        st.session_state.spots.append({
            "name": s_name,
            "lat": vip_lat + s_lat,
            "lng": vip_lng + s_lng,
            "level": level_dict[s_level],
            "color": color_dict[s_level],
            "type": s_type
        })
        t_str = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.insert(0, f"[{t_str}] [현장 제보] {s_name} ({s_type}) 등록")
        st.sidebar.success("등록 완료되었습니다.")

st.title("🛡️ 스마트 VIP 경호 및 세이프 루트 시스템")
st.caption("실시간 파파라치·사생팬 감지 / 100m 이내 반경 경고 / 자동 우회 동선")

min_dist = float("inf")
closest = None

for s in st.session_state.spots:
    d = get_distance(vip_lat, vip_lng, s["lat"], s["lng"])
    if d < min_dist:
        min_dist = d
        closest = s

col1, col2 = st.columns([2, 1])

with col1:
    if closest and min_dist <= 100:
        st.markdown(f"""
        <div class="alert-box-danger">
            🚨 [긴급 경고 - 100m 이내 위협 감지!]<br>
            근접 위협: <b>{closest['name']}</b> ({closest['type']}) | 거리: <b>{min_dist:.1f}m</b><br>
            📱 스마트폰 및 스마트워치 긴급 진동/알림 발송 완료!<br>
            👉 하단 세이프 루트(녹색 점선)로 즉시 이동하십시오.
        </div>
        """, unsafe_allow_html=True)
    elif closest:
        st.markdown(f"""
        <div class="alert-box-safe">
            ✅ [안전 상태] 최단 거리 위협: <b>{closest['name']}</b> ({min_dist:.1f}m 거리)<br>
            주변 경로가 안전합니다. 기존 동선을 유지하세요.
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.metric(label="VIP 차량 속도", value="34 km/h")
    st.metric(label="감지된 위협 수", value=f"{len(st.session_state.spots)} 곳")

st.markdown("---")

t1, t2, t3 = st.tabs(["🗺️ 위험 지도 & 세이프 루트", "🔥 시간대별 히트맵", "🤖 AI 경호 리포트"])

# 지도 레이어 속성 추가 (오류 해결)
ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
TILES = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'

with t1:
    m_col, i_col = st.columns([3, 2])
    
    with m_col:
        st.subheader("📍 실시간 감지 지도")
        m = folium.Map(location=[vip_lat, vip_lng], zoom_start=16, tiles=TILES, attr=ATTR)
        
        folium.Marker(
            [vip_lat, vip_lng],
            popup="VIP 차량",
            tooltip="VIP 차량",
            icon=folium.Icon(color="blue", icon="car", prefix="fa")
        ).add_to(m)
        
        folium.Circle(
            location=[vip_lat, vip_lng],
            radius=100,
            color="cyan",
            weight=1.5,
            fill=True,
            fill_opacity=0.1
        ).add_to(m)

        for s in st.session_state.spots:
            folium.Marker(
                [s["lat"], s["lng"]],
                popup=f"<b>{s['name']}</b><br>유형: {s['type']}",
                tooltip=f"[{s['level']}] {s['name']}",
                icon=folium.Icon(color=s["color"], icon="exclamation-triangle", prefix="fa")
            ).add_to(m)
            folium.Circle(
                location=[s["lat"], s["lng"]],
                radius=40,
                color=s["color"],
                fill=True,
                fill_opacity=0.3
            ).add_to(m)

        safe_dest = [vip_lat - 0.003, vip_lng - 0.003]
        safe_line = [
            [vip_lat, vip_lng],
            [vip_lat - 0.001, vip_lng - 0.0005],
            [vip_lat - 0.002, vip_lng - 0.002],
            safe_dest
        ]
        folium.PolyLine(
            safe_line,
            color="#00FF7F",
            weight=5,
            opacity=0.8,
            dash_array="10",
            tooltip="🟢 추천 세이프 루트"
        ).add_to(m)
        
        folium.Marker(
            safe_dest,
            popup="비공개 지하 주차장 B3",
            tooltip="🔒 세이프존 (지하 엘리베이터)",
            icon=folium.Icon(color="green", icon="shield", prefix="fa")
        ).add_to(m)

        st_folium(m, width="100%", height=450, key="sec_map")

    with i_col:
        st.subheader("🛡️ 세이프 루트 안내")
        st.info("🚨 **회피 구역**: 청담동 대로변 & 정문 로비")
        st.success("🟢 **우회 동선**: 건물 뒷골목 B구역 ➔ 비공개 지하 주차장 B3")
        
        st.subheader("📡 감지 및 제보 로그")
        log_box = st.container(height=230)
        with log_box:
            for l in st.session_state.logs:
                st.write(l)

with t2:
    st.subheader("📊 과거 누적 출몰 히트맵")
    h_col1, h_col2 = st.columns([1, 3])
    
    with h_col1:
        sel_hour = st.slider("시간대 (시)", 0, 23, 18)
        st.write(f"선택 시간: **{sel_hour:02d}:00**")
    
    with h_col2:
        np.random.seed(sel_hour)
        pts = 40 + (sel_hour % 6) * 15
        h_lats = np.random.normal(BASE_LAT, 0.003, pts)
        h_lngs = np.random.normal(BASE_LNG, 0.003, pts)
        h_weights = np.random.uniform(0.3, 1.0, pts)
        
        heat_data = list(zip(h_lats, h_lngs, h_weights))
        hm = folium.Map(location=[BASE_LAT, BASE_LNG], zoom_start=15, tiles=TILES, attr=ATTR)
        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(hm)
        st_folium(hm, width="100%", height=400, key="heat_map")

with t3:
    st.subheader("🤖 Gemini AI 경호 브리핑")
    if st.button("✨ Gemini AI 브리핑 리포트 생성"):
        with st.spinner("AI 분석 중..."):
            rep = get_ai_report(st.session_state.spots, vip_lat, vip_lng, min_dist)
            st.markdown("---")
            st.markdown(rep)
