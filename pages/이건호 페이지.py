import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime
import json

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="VIP Smart Security AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1e222d;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
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

# -----------------------------------------------------------------------------
# 2. Helper Functions & Initial State
# -----------------------------------------------------------------------------
# 기준 위치: 서울 강남구 청담동 주변 (VIP 이동 빈도 높음)
BASE_LAT, BASE_LNG = 37.5240, 127.0425

def init_session_state():
    if "spots" not in st.session_state:
        st.session_state.spots = [
            {"name": "청담동 메인 대로변", "lat": 37.5252, "lng": 127.0435, "level": "위험", "color": "red", "type": "파파라치 밀집", "auto": True},
            {"name": "주출입구 정문 로비", "lat": 37.5245, "lng": 127.0415, "level": "경고", "color": "orange", "type": "사생팬 진을 침", "auto": False},
            {"name": "건물 앞 수상한 밴 차량", "lat": 37.5230, "lng": 127.0440, "level": "주의", "color": "yellow", "type": "장기 체류 차량", "auto": True},
        ]
    if "logs" not in st.session_state:
        st.session_state.logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] [AI 감지] 렌즈 반사 신호 자동 탐지 (청담동 메인 대로변)",
            f"[{datetime.now().strftime('%H:%M:%S')}] [경호원 제보] 정문 로비 사생팬 10여 명 대기 중",
        ]

init_session_state()

def calculate_distance(lat1, lon1, lat2, lon2):
    # 하버사인 공식을 통한 미터 단위 거리 계산
    R = 6371000  # 지구 반지름 (m)
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi/2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

# Gemini AI 분석 함수
def analyze_security_threats(spots, vip_lat, vip_lng, min_dist):
    try:
        from google import genai
        
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ Gemini API 키가 설정되지 않았습니다. Secrets에 GEMINI_API_KEY를 등록해주세요."

        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        당신은 연예인 전문 최고 레벨의 AI 경호 팀장입니다.
        현재 VIP 차량 위치: (위도: {vip_lat}, 경도: {vip_lng})
        가장 가까운 위협과의 거리: {min_dist:.1f}m
        현재 감지된 위협 스팟 목록: {json.dumps(spots, ensure_ascii=False)}

        위 데이터를 바탕으로 현장 경호원 및 매니저에게 전달할 '실시간 경호 브리핑 및 행동 수칙'을 작성해 주세요.
        다음 내용을 포함해야 합니다:
        1. 현재 위협 수준 평가
        2. 최우선 회피 조치 및 세이프 루트 이용 지침
        3. 현장 경호원 긴급 대응 행동 수칙 (3가지)
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI 리포트 생성 중 오류가 발생했습니다: {str(e)}"

# -----------------------------------------------------------------------------
# 3. Sidebar: Control Panel & Manual Spot Add
# -----------------------------------------------------------------------------
st.sidebar.title("🛡️ 스마트 경호 관제 센터")
st.sidebar.subheader("🚗 VIP 차량 위치 시뮬레이션")

vip_lat = st.sidebar.slider("VIP 위도", 37.5200, 37.5280, BASE_LAT, format="%.4f")
vip_lng = st.sidebar.slider("VIP 경도", 127.0380, 127.0460, BASE_LNG, format="%.4f")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 수동 위협 제보 등록")
with st.sidebar.form("add_spot_form", clear_on_submit=True):
    spot_name = st.text_input("위치/장소명", "건물 후문 골목길")
    threat_type = st.selectbox("위협 유형", ["파파라치 밀집", "의심 차량 대기", "사생팬 진을 침", "드론 촬영 감지"])
    level = st.selectbox("위험 단계", ["주의 (노란색)", "경고 (주황색)", "위험 (빨간색)"])
    rel_lat = st.number_input("위도 오프셋", -0.005, 0.005, 0.001, step=0.0005, format="%.4f")
    rel_lng = st.number_input("경도 오프셋", -0.005, 0.005, -0.001, step=0.0005, format="%.4f")
    
    submitted = st.form_submit_button("신규 스팟 제보 등록")
    if submitted:
        color_map = {"주의 (노란색)": "yellow", "경고 (주황색)": "orange", "위험 (빨간색)": "red"}
        level_map = {"주의 (노란색)": "주의", "경고 (주황색)": "경고", "위험 (빨간색)": "위험"}
        
        new_spot = {
            "name": spot_name,
            "lat": vip_lat + rel_lat,
            "lng": vip_lng + rel_lng,
            "level": level_map[level],
            "color": color_map[level],
            "type": threat_type,
            "auto": False
        }
        st.session_state.spots.append(new_spot)
        st.session_state.logs.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] [현장 제보] {spot_name} ({threat_type}) 등록됨")
        st.sidebar.success("새로운 위협 스팟이 지도에 등록되었습니다.")

# -----------------------------------------------------------------------------
# 4. Main UI Header & Distance Alert Engine
# -----------------------------------------------------------------------------
st.title("🛡️ Smart VIP Security AI Monitor")
st.caption("AI 기반 파파라치·의심 차량 실시간 감지 및 대피 세이프 루트 안내 시스템")

# 가장 가까운 위험 스팟과의 거리 계산
min_distance = float("inf")
closest_spot = None

for spot in st.session_state.spots:
    dist = calculate_distance(vip_lat, vip_lng, spot["lat"], spot["lng"])
    if dist < min_distance:
        min_distance = dist
        closest_spot = spot

# 100m 이내 진입 시 긴급 알림 경고
col_alert1, col_alert2 = st.columns([2, 1])

with col_alert1:
    if min_distance <= 100:
        st.markdown(f"""
        <div class="alert-box-danger">
            🚨 [긴급 경고 - 반경 100m 이내 위협 진입!]<br>
            근접 위협: <b>{closest_spot['name']}</b> ({closest_spot['type']}) | 거리: <b>{min_distance:.1f}m</b><br>
            📱 스마트폰 및 스마트워치 긴급 진동 및 팝업 발송됨!<br>
            👉 AI 세이프 루트(우회 동선)로 즉시 회피하십시오.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-box-safe">
            ✅ [안전 상태] 최단 거리 위협: <b>{closest_spot['name']}</b> ({min_distance:.1f}m 떨어진 위치)<br>
            VIP 이동 경로상 특이 위협 경고가 없습니다. 안전 동선을 유지하세요.
        </div>
        """, unsafe_allow_html=True)

with col_alert2:
    st.metric(label="현재 VIP 이동 속도 (추정)", value="34 km/h")
    st.metric(label="감지된 총 위험 스팟", value=f"{len(st.session_state.spots)} 개 구역")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. Main Content Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🗺️ 실시간 지도 & 세이프 루트", "🔥 시간대별 히트맵 분석", "🤖 AI 경호 리포트"])

# TAB 1: 실시간 지도 & 세이프 루트
with tab1:
    col_map, col_info = st.columns([3, 2])
    
    with col_map:
        st.subheader("📍 실시간 감지 지도 & 우회 세이프 루트")
        
        # Folium 지도 생성
        m = folium.Map(location=[vip_lat, vip_lng], zoom_start=16, tiles="cartodbpositrondarkmatter")
        
        # VIP 위치 마커
        folium.Marker(
            [vip_lat, vip_lng],
            popup="VIP 및 매니저 차량",
            tooltip="VIP 차량 (현재 위치)",
            icon=folium.Icon(color="blue", icon="car", prefix="fa")
        ).add_to(m)
        
        # 100m 위험 반경 표시 (원)
        folium.Circle(
            location=[vip_lat, vip_lng],
            radius=100,
            color="cyan",
            weight=1.5,
            fill=True,
            fill_opacity=0.1,
            popup="100m 경고 감지 반경"
        ).add_to(m)

        # 위험 스팟 마커 추가
        for spot in st.session_state.spots:
            folium.Marker(
                [spot["lat"], spot["lng"]],
                popup=f"<b>{spot['name']}</b><br>유형: {spot['type']}<br>단계: {spot['level']}",
                tooltip=f"[{spot['level']}] {spot['name']}",
                icon=folium.Icon(color=spot["color"], icon="exclamation-triangle", prefix="fa")
            ).add_to(m)
            
            # 위험/경고 지역 반경 Circle
            folium.Circle(
                location=[spot["lat"], spot["lng"]],
                radius=40,
                color=spot["color"],
                fill=True,
                fill_opacity=0.3
            ).add_to(m)

        # 우회 세이프 루트 시뮬레이션 경로 (대로변 회피 -> 지하 주차장/후문)
        safe_destination = [vip_lat - 0.003, vip_lng - 0.003] # 보안 확보된 지하 주차장
        safe_route_coords = [
            [vip_lat, vip_lng],
            [vip_lat - 0.001, vip_lng - 0.0005],
            [vip_lat - 0.002, vip_lng - 0.002],
            safe_destination
        ]
        
        # 세이프 루트 표시 (녹색 점선)
        folium.PolyLine(
            safe_route_coords,
            color="#00FF7F",
            weight=5,
            opacity=0.8,
            dash_array="10",
            tooltip="🟢 AI 추천 세이프 루트 (비공개 후문/지하 주차장)"
        ).add_to(m)
        
        folium.Marker(
            safe_destination,
            popup="보안 확보된 지하 주차장 B3 (비공개 엘리베이터 연동)",
            tooltip="🔒 세이프존 도착지",
            icon=folium.Icon(color="green", icon="shield", prefix="fa")
        ).add_to(m)

        # 지도 출력
        st_folium(m, width="100%", height=480)

    with col_info:
        st.subheader("🛡️ AI 세이프 루트 경로 안내")
        st.info("🚨 **회피구역**: 청담동 메인 대로변 & 정문 로비 (파파라치 및 사생팬 밀집)")
        st.success("🟢 **우회 동선**: 건물 뒷골목 B구역 ➔ 비공개 지하 주차장 B3 ➔ 전용 엘리베이터")
        
        st.subheader("📡 자동 감지 & 제보 데이터 실시간 로그")
        log_container = st.container(height=250)
        with log_container:
            for log in st.session_state.logs:
                st.write(log)
        
        if st.button("🗑️ 로그 및 스팟 초기화"):
            st.session_state.clear()
            init_session_state()
            st.rerun()

# TAB 2: 시간대별 히트맵 분석
with tab2:
    st.subheader("📊 과거 데이터 누적 시간대별 파파라치 출몰 히트맵")
    st.caption("사전 이동 계획 수립을 위한 위험 패턴 예측 분석")
    
    col_time, col_heat = st.columns([1, 3])
    
    with col_time:
        selected_hour = st.slider("시간대 선택 (00시 ~ 23시)", 0, 23, 18)
        st.write(f"현재 선택된 시간: **{selected_hour:02d}:00**")
        st.markdown("""
        **💡 분석 팁:**
        - **14시~16시**: 퇴근길 소속사 주변 차량 밀집
        - **18시~22시**: 방송국 및 촬영장 출몰 확률 **최고 (빨간색)**
        - **23시~02시**: 심야 사적 모임 장소 추적 주의
        """)

    with col_heat:
        # 시간대별 난수 발생을 통해 히트맵 시뮬레이션 데이터 생성
        np.random.seed(selected_hour)
        num_points = 50 + (selected_hour % 5) * 20
        
        # 중심점 주변 가우시안 분포
        lats = np.random.normal(BASE_LAT, 0.003, num_points)
        lngs = np.random.normal(BASE_LNG, 0.003, num_points)
        weights = np.random.uniform(0.3, 1.0, num_points)
        
        heat_data = list(zip(lats, lngs, weights))
        
        m_heat = folium.Map(location=[BASE_LAT, BASE_LNG], zoom_start=15, tiles="cartodbpositrondarkmatter")
        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m_heat)
        
        st_folium(m_heat, width="100%", height=400, key="heatmap")

# TAB 3: AI 경호 리포트 (Gemini 2.5 Flash Lite)
with tab3:
    st.subheader("🤖 Gemini AI 실시간 경호 브리핑")
    st.write("현재 스팟 데이터와 VIP 위치를 분석하여 현장 경호팀에게 즉시 공유할 브리핑 문
