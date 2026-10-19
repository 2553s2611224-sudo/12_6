import os
import time
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="VIP GuardAI - 스마트 경호관제 시스템",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0f1117;
    }
    .stAlert {
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. State & Session Management
# ---------------------------------------------------------
# 기본 중심 좌표 (서울 Gangnam/Cheongdam area)
BASE_LAT = 37.5250
BASE_LON = 127.0400

if "spots" not in st.session_state:
    st.session_state.spots = pd.DataFrame([
        {"id": 1, "name": "청담동 A 기획사 사옥 정문", "lat": 37.5260, "lon": 127.0390, "level": "위험", "desc": "사생팬 15명 대기, 대형 망원렌즈 카메라 3대 감지", "type": "자동(렌즈반사)"},
        {"id": 2, "name": "압구정 B 미용실 주차장 입구", "lat": 37.5235, "lon": 127.0380, "level": "경고", "desc": "의심 밴 차량 20분 이상 장기 주차 중", "type": "자동(장기체류)"},
        {"id": 3, "name": "C 카페 후문 골목길", "lat": 37.5242, "lon": 127.0420, "level": "주의", "desc": "파파라치 추정 인원 2명 이동 중", "type": "수동(경호원)"}
    ])

if "vip_location" not in st.session_state:
    st.session_state.vip_location = {"lat": 37.5252, "lon": 127.0392}


# ---------------------------------------------------------
# 3. Helper Functions
# ---------------------------------------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    """두 지점 간 거리 계산 (단위: 미터)"""
    R = 6371000  # 지구 반지름 (미터)
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def get_color_by_level(level):
    """위험 단계별 RGB 색상 지정"""
    if level == "위험":
        return [255, 0, 0, 180]      # 빨간색
    elif level == "경고":
        return [255, 140, 0, 180]    # 주황색
    else:
        return [255, 215, 0, 180]    # 노란색

def call_gemini_risk_analysis(location_name, visit_time, context_info):
    """Gemini API를 이용한 위험도 예측 및 사전 대비책 생성"""
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Secrets에 `GEMINI_API_KEY`가 설정되지 않아 AI 예측을 실행할 수 없습니다."
    
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        당신은 최고 수준의 VIP 경호 전략 AI입니다.
        아래 상황 정보를 바탕으로 파파라치/사생팬 위험도를 평가하고, 방문 전 경호팀이 이행해야 할 **사전 대비책 3가지**를 명확하고 간결하게 제시하세요.

        - 방문 예정 장소: {location_name}
        - 방문 예정 시간: {visit_time}
        - 특이사항 및 주변 환경: {context_info}

        [응답 형식]
        1. 🎯 종합 위험도 평가 (낮음/보통/높음/매우높음) 및 이유
        2. 🛡️ 사전 경호 및 대피 수칙 (3가지 항목)
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text
    except Exception as e:
        return f"❌ AI 분석 중 오류가 발생했습니다: {str(e)}"


# ---------------------------------------------------------
# 4. Sidebar Controls
# ---------------------------------------------------------
st.sidebar.title("🛡️ VIP GuardAI")
st.sidebar.caption("실시간 경호 관제 & 세이프 루트 안내")
st.sidebar.divider()

menu = st.sidebar.radio(
    "메뉴 선택",
    ["관제 대시보드 및 세이프 루트", "실시간 위험 제보 / AI 감지", "시간대별 위험 히트맵 & AI 예측"]
)

st.sidebar.divider()
st.sidebar.subheader("🚗 VIP 차량 위치 조절 (시뮬레이션)")
vip_lat = st.sidebar.slider("VIP 위도 (Lat)", 37.5200, 37.5300, st.session_state.vip_location["lat"], format="%.4f")
vip_lon = st.sidebar.slider("VIP 경도 (Lon)", 127.0300, 127.0500, st.session_state.vip_location["lon"], format="%.4f")
st.session_state.vip_location = {"lat": vip_lat, "lon": vip_lon}


# ---------------------------------------------------------
# 5. Main Screen Render
# ---------------------------------------------------------

# ===== MENU 1: 관제 대시보드 및 세이프 루트 =====
if menu == "관제 대시보드 및 세이프 루트":
    st.title("🚨 실시간 관제 및 AI 세이프 루트")
    
    # VIP 차량과 위험 스팟 간 거리 계산 & 100m 이내 진입 경보 체크
    alerts = []
    df_spots = st.session_state.spots.copy()
    
    for idx, row in df_spots.iterrows():
        dist = calculate_distance(vip_lat, vip_lon, row['lat'], row['lon'])
        df_spots.loc[idx, 'distance'] = dist
        if dist <= 100:
            alerts.append((row['name'], row['level'], int(dist)))

    # 팝업 및 진동 경고 시뮬레이션
    if alerts:
        for spot_name, level, d in alerts:
            st.error(f"⚠️ **[즉시 경고 - 100m 이내 진입]** {spot_name} ({level} 스팟)이 약 {d}m 거리에 있습니다! 스마트폰/스마트워치 진동 경고 발송됨.")
        st.toast("🚨 경고: 위험 스팟 100m 이내 진입! 세이프 루트로 전환합니다.", icon="🔔")

    # 상단 요약 지표 (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VIP 차량 상태", "이동 중" if not alerts else "대피 경로 진입", delta="경계 상태" if alerts else "안전")
    col2.metric("위험(빨강) 스팟", f"{len(df_spots[df_spots['level']=='위험'])} 곳")
    col3.metric("경고(주황) 스팟", f"{len(df_spots[df_spots['level']=='경고'])} 곳")
    col4.metric("주의(노랑) 스팟", f"{len(df_spots[df_spots['level']=='주의'])} 곳")

    st.subheader("🗺️ 실시간 위험 지도 및 대피 동선 시각화")

    # Pydeck 지도 데이터 준비
    df_spots['color'] = df_spots['level'].apply(get_color_by_level)
    
    # 스팟 원형 레이어
    spot_layer = pdk.Layer(
        "ScatterplotLayer",
        df_spots,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=80,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        get_line_color=[255, 255, 255],
        get_line_width=3
    )

    # VIP 차량 레이어
    vip_df = pd.DataFrame([{"lat": vip_lat, "lon": vip_lon, "name": "VIP 차량" if not alerts else "VIP 차량 (대피 중)"}])
    vip_layer = pdk.Layer(
        "ScatterplotLayer",
        vip_df,
        get_position=["lon", "lat"],
        get_color=[0, 150, 255, 255] if not alerts else [255, 0, 100, 255],
        get_radius=50,
        pickable=True
    )

    # AI 세이프 루트 경로 생성 시뮬레이션 (위험 시 우회 경로, 평시 일반 경로)
    if alerts:
        # 대로변 회피 -> 건물 후문 / 지하 비공개 엘리베이터 이동 우회 동선
        path_data = [{
            "path": [
                [vip_lon, vip_lat],
                [vip_lon + 0.001, vip_lat - 0.001],
                [vip_lon + 0.002, vip_lat + 0.0005],  # 후문 비공개 통로
            ]
        }]
        path_color = [0, 255, 150] # 안전 그린
    else:
        path_data = [{
            "path": [
                [vip_lon, vip_lat],
                [vip_lon + 0.003, vip_lat + 0.002]
            ]
        }]
        path_color = [100, 100, 255]

    path_layer = pdk.Layer(
        "PathLayer",
        path_data,
        get_path="path",
        get_color=path_color,
        width_min_pixels=5,
    )

    view_state = pdk.ViewState(
        latitude=vip_lat,
        longitude=vip_lon,
        zoom=15,
        pitch=40
    )

    r = pdk.Deck(
        layers=[spot_layer, vip_layer, path_layer],
        initial_view_state=view_state,
        tooltip={"html": "<b>{name}</b><br/>단계: {level}<br/>설명: {desc}"}
    )
    st.pydeck_chart(r)

    # 세이프 루트 실시간 안내
    st.markdown("### 🧭 AI 실시간 동선 안내 (Navigation)")
    if alerts:
        st.error("🚨 **[AI 세이프 루트 가동]** 대로변 및 주 출입구 파파라치 밀집으로 인해 우회 동선을 생성했습니다.")
        st.markdown("""
        * **1단계:** 100m 앞 교차로에서 우회전하여 **건물 후문 비공개 골목**으로 진입하세요.
        * **2단계:** 지하 2층 **VIP 전용 비공개 엘리베이터 라인**으로 직행하세요.
        * **3단계:** 보안 요원이 후문 통로 통제를 완료했습니다.
        """)
    else:
        st.success("✅ **[정상 경로 진행]** 주변 100m 내 위협 요소가 없습니다. 기존 이동 동선을 유지하세요.")

    # 스팟 리스트 표
    st.markdown("### 📋 감지된 위험 스팟 목록")
    st.dataframe(
        df_spots[['name', 'level', 'type', 'desc', 'distance']].rename(columns={
            'name': '스팟명', 'level': '위험도', 'type': '등록 방식', 'desc': '상세 상황', 'distance': 'VIP와의 거리(m)'
        }),
        use_container_width=True
    )


# ===== MENU 2: 실시간 위험 제보 / AI 감지 =====
elif menu == "실시간 위험 제보 / AI 감지":
    st.title("🚨 실시간 위험 스팟 등록 및 감지")
    
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📱 현장 경호원 / 관계자 제보 등록")
        with st.form("manual_report_form"):
            spot_name = st.text_input("스팟 위치/장소명", value="D 빌딩 후문 주차장")
            level = st.selectbox("위험 단계", ["주의", "경고", "위험"])
            desc = st.text_area("현장 상세 설명", value="의심 차량 1대 대기 중, 내부 촬영 장비 확인")
            lat_offset = st.number_input("위도 오프셋 (테스트용)", value=0.001, format="%.4f")
            lon_offset = st.number_input("경도 오프셋 (테스트용)", value=-0.001, format="%.4f")
            
            submit_btn = st.form_submit_button("제보 등록")
            if submit_btn:
                new_id = len(st.session_state.spots) + 1
                new_spot = {
                    "id": new_id,
                    "name": spot_name,
                    "lat": BASE_LAT + lat_offset,
                    "lon": BASE_LON + lon_offset,
                    "level": level,
                    "desc": desc,
                    "type": "수동(경호원)"
                }
                st.session_state.spots = pd.concat([st.session_state.spots, pd.DataFrame([new_spot])], ignore_index=True)
                st.success(f"✅ '{spot_name}' 스팟이 성공적으로 등록되었습니다.")
                st.rerun()

    with col_right:
        st.subheader("🤖 AI 자동 감지 시뮬레이션")
        st.info("광학 센서 및 블랙박스 AI가 카메라 렌즈 반사 신호나 장기 체류 인원을 자동 감지합니다.")
        
        sensor_type = st.radio("센서 감지 이벤트 선택", ["렌즈 반사 신호 감지 (카메라)", "동일 장소 장기 체류 감지 (의심 인원/차량)"])
        
        if st.button("⚡ AI 자동 감지 신호 발생 시뮬레이션"):
            with st.spinner("AI 분석 및 자동 스팟 등록 중..."):
                time.sleep(1)
                new_id = len(st.session_state.spots) + 1
                if "렌즈 반사" in sensor_type:
                    auto_spot = {
                        "id": new_id,
                        "name": "E 쇼핑몰 건너편 2층 창가",
                        "lat": BASE_LAT - 0.0015,
                        "lon": BASE_LON + 0.0012,
                        "level": "위험",
                        "desc": "AI 카메라 센서가 70-200mm 망원 렌즈 반사 신호 2건 자동 감지",
                        "type": "자동(렌즈반사)"
                    }
                else:
                    auto_spot = {
                        "id": new_id,
                        "name": "F 골목길 입구",
                        "lat": BASE_LAT + 0.0022,
                        "lon": BASE_LON - 0.0008,
                        "level": "경고",
                        "desc": "블랙박스 AI가 동일 인원 45분 이상 서성임 감지",
                        "type": "자동(장기체류)"
                    }
                st.session_state.spots = pd.concat([st.session_state.spots, pd.DataFrame([auto_spot])], ignore_index=True)
                st.success(f"🤖 [AI 자동 등록 완료] {auto_spot['name']} ({auto_spot['level']})")
                st.rerun()


# ===== MENU 3: 시간대별 위험 히트맵 & AI 예측 =====
elif menu == "시간대별 위험 히트맵 & AI 예측":
    st.title("🔥 과거 출몰 히트맵 & Gemini AI 분석")

    tab1, tab2 = st.tabs(["🔥 시간대별 파파라치 출몰 히트맵", "🤖 Gemini AI 사전 위험도 예측"])

    with tab1:
        st.subheader("📊 과거 파파라치/사생팬 누적 데이터 히트맵")
        selected_time = st.select_slider(
            "분석 시간대 선택",
            options=["00:00~06:00 (새벽)", "06:00~12:00 (오전)", "12:00~18:00 (오후)", "18:00~24:00 (야간)"]
        )

        # 시간대별 샘플 히트맵 데이터 생성
        np.random.seed(len(selected_time))
        heatmap_data = pd.DataFrame({
            'lat': BASE_LAT + np.random.normal(0, 0.003, 100),
            'lon': BASE_LON + np.random.normal(0, 0.003, 100),
            'weight': np.random.uniform(0.1, 1.0, 100)
        })

        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            heatmap_data,
            get_position=["lon", "lat"],
            get_weight="weight",
            radius_pixels=60,
        )

        r_heatmap = pdk.Deck(
            layers=[heatmap_layer],
            initial_view_state=pdk.ViewState(
                latitude=BASE_LAT,
                longitude=BASE_LON,
                zoom=14,
                pitch=30
            )
        )
        st.pydeck_chart(r_heatmap)
        st.caption(f"📌 {selected_time} 시간대에 파파라치가 자주 출몰한 핫스팟 지역입니다. 해당 시간대 이동 시 주의하세요.")

    with tab2:
        st.subheader("🤖 Gemini 2.5 Flash Lite 사전 위험 예측 및 경호 수칙")
        st.write("방문 예정 장소와 시간대를 입력하면 AI가 사전 위험도를 평가하고 맞춤형 경호 대비책을 작성합니다.")

        col_a, col_b = st.columns(2)
        with col_a:
            target_location = st.text_input("방문 예정 장소", value="성수동 K-POP 팝업스토어 행사장")
            target_time = st.text_input("방문 예정 시간", value="금요일 오후 6시 30분 (퇴근 시간대)")
        with col_b:
            target_context = st.text_area("주변 환경 및 상황", value="공개 행사로 언론 보도됨, 주 출입구 앞 인도 협소, 비공개 주차장 이용 불가")

        if st.button("🔮 AI 위험도 예측 및 대비책 수립"):
            with st.spinner("Gemini AI가 위험 요소를 분석하는 중입니다..."):
                result = call_gemini_risk_analysis(target_location, target_time, target_context)
                st.markdown("---")
                st.markdown("### 📋 AI 경호 브리핑 리포트")
                st.markdown(result)
