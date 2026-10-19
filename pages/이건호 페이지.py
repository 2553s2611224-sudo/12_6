import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime
import json

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 디자인 CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="스마트 VIP 경호 및 세이프 루트",
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
# 2. 초기 상태 및 도우미 함수
# -----------------------------------------------------------------------------
BASE_LAT, BASE_LNG = 37.5240, 127.0425  # 기본 위치 (청담동 부근)

if "spots" not in st.session_state:
    st.session_state.spots = [
        {"name": "청담동 메인 대로변", "lat": 37.5252, "lng": 127.0435, "level": "위험", "color": "red", "type": "파파라치 밀집", "auto": True},
        {"name": "주출입구 정문 로비", "lat": 37.5245, "lng": 127.0415, "level": "경고", "color": "orange", "type": "사생팬 대기 중", "auto": False},
        {"name": "건물 앞 수상한 밴 차량", "lat": 37.5230, "lng": 127.0440, "level": "주의", "color": "yellow", "type": "장기 체류 차량", "auto": True},
    ]

if "logs" not in st.session_state:
    now_str = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs = [
        f"[{now_str}] [AI 감지] 렌즈 반사 신호 자동 탐지 (청담동 메인 대로변)",
        f"[{now_str}] [경호원 제보] 정문 로비 사생팬 10여 명 대기 중",
    ]

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000.0  # 지구 반지름 (m)
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return float(R * c)

def analyze_security_threats(spots, vip_lat, vip_lng, min_dist):
    try:
        from google import genai
        
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return "⚠️ Gemini API 키가 설정되지 않았습니다. Secrets에 GEMINI_API_KEY를 등록해 주세요."

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
# 3. 사이드바 관제 및 제보 입력
# -----------------------------------------------------------------------------
st.sidebar.title("🛡️ 스마트 경호 관제")
st.sidebar.subheader("🚗 VIP 차량 위치 조절")

vip_lat = st.sidebar.slider("VIP 위도", 37.5200, 37.5280, BASE_LAT, format="%.4f")
vip_lng = st.sidebar.slider("VIP 경도", 127.0380, 127.0460, BASE_LNG, format="%.4f")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 수동 위협 제보 등록")
with st.sidebar.form("add_spot_form", clear_on_submit=True):
    spot_name = st.text_input("위치/장소명", "건물 후문 골목길")
    threat_type = st.selectbox("위협 유형", ["파파라치 밀집", "의심 차량 대기", "사생팬 대기 중", "드론 촬영 감지"])
    level = st.selectbox("위험 단계", ["주의 (노란색)", "경고 (주황색)", "위험 (빨간색)"])
    rel_lat = st.number_input("위도 위치 조정", -0.005, 0.005, 0.001, step=0.0005, format="%.4f")
    rel_lng = st.number_input("경도 위치 조정", -0.005, 0.005, -0.001, step=0.0005, format="%.4f")
    
    submitted = st.form_submit_button("신규 스팟 등록")
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
        now_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.insert(0, f"[{now_time}] [현장 제보] {spot_name} ({threat_type}) 등록됨")
        st.sidebar.success("위협 스팟이 지도에 등록되었습니다.")

# -----------------------------------------------------------------------------
# 4. 메인 화면 및 실시간 거리 계산 경고
# -----------------------------------------------------------------------------
st.title("🛡️ 스마트 VIP 경호 및 세이프 루트 안내 시스템")
st.caption("촬영·추적 감지 / 100m 이내 반경 경고 / 우회 동선 자동 제공")

min_distance = float("inf")
closest_spot = None

for spot in st.session_state.spots:
    dist = calculate_distance(vip_lat, vip_lng, spot["lat"], spot["lng"])
    if dist < min_distance:
        min_distance = dist
        closest_spot = spot

col_alert1, col_alert2 = st.columns([2, 1])

with col_alert1:
    if closest_spot and min_distance <= 100:
        st.markdown(f"""
        <div class="alert-box-danger">
            🚨 [긴급 경고 - 반경 100m 이내 위협 진입!]<br>
            근접 위협 장소: <b>{closest_spot['name']}</b> ({closest_spot['type']}) | 거리: <b>{min_distance:.
