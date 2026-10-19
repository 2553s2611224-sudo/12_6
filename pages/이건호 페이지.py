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

def get_ai_report(spots, v
