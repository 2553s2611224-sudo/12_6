import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import os
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 스타일 지정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Paparazzi Escape - VIP 경호 관제",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 다크 모드 스타일 custom CSS
st.markdown("""
<style>
    .main-title {
        color: #FF4B4B;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #FAFAFA;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    .alert-card {
        background-color: #2b1113;
        border: 1px solid #ff4b4b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Gemini API 설정 (secrets 및 환경 변수 안전 처리)
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

ai_enabled = False
if api_key:
    try:
        genai.configure(api_key=api_key)
        # 요구사항에 명시된 gemini-2.5-flash-lite 사용
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        ai_enabled = True
    except Exception as e:
        st.warning(f"Gemini API 설정 중 오류가 발생했습니다: {e}")
else:
    st.info("💡 API 키가 등록되지 않아 기본 시나리오 모드로 작동합니다. AI 기능을 이용하려면 Secrets에 GEMINI_API_KEY를 등록하세요.")

# -----------------------------------------------------------------------------
# 3. 사이드바 - 관제 설정 및 상태 선택
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/emoji/96/000000/police-car-light.png", width=70)
st.sidebar.title("VIP 관제 센터")

vip_name = st.sidebar.text_input("VIP 아티스트 이름", value="강해린 (Star)")
threat_level = st.sidebar.selectbox("현재 위협 단계", ["⚠️ 경계 (Caution)", "🚨 심각 (Danger)", "🟢 안전 (Clear)"], index=1)
paparazzi_count = st.sidebar.slider("포착된 파파라치 수", min_value=1, max_value=20, value=7)
escort_team = st.sidebar.selectbox("배치된 경호팀", ["Alpha 팀 (차량 2대)", "Bravo 팀 (오토바이 3대)", "Charlie 팀 (지상/헬기)"])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 실시간 위협 위치 레이더 갱신"):
    st.rerun()

# -----------------------------------------------------------------------------
# 4. 메인 화면 - 헤더 및 상태 메트릭
# -----------------------------------------------------------------------------
st.markdown(f"<div class='main-title'>🚨 VIP [{vip_name}] 실시간 경호 관제 센터</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>파파라치 추적 추적 및 실시간 대피 상황 종합 대시보드</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="현재 상태", value=threat_level.split()[1], delta="- 위협 수준 고조" if "심각" in threat_level else "안정")
with col2:
    st.metric(label="추적 중인 파파라치", value=f"{paparazzi_count} 기", delta=f"+{np.random.randint(1, 3)}기 접근 중", delta_color="inverse")
with col3:
    st.metric(label="경호팀 도착 예정 시간", value="1분 30초", delta="-30초 단축")
with col4:
    st.metric(label="최적 대피로 확보율", value="78%", delta="12%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 메인 레이아웃: 파파라치 지도 시각화 & 실시간 제어
# -----------------------------------------------------------------------------
left_col, right_col = st.columns([7, 5])

with left_col:
    st.subheader("📡 실시간 파파라치 추적 레이더 지도")
    
    # 가상의 GPS 데이터 생성 (VIP, 파파라치, 경호원)
    np.random.seed(42)
    
    # VIP 위치 (중심)
    vip_lat, vip_lon = 37.5665, 126.9780
    
    # 파파라치 위치 (VIP 주변 임의 산출)
    p_lats = vip_lat + np.random.uniform(-0.008, 0.008, paparazzi_count)
    p_lons = vip_lon + np.random.uniform(-0.008, 0.008, paparazzi_count)
    
    # 경호원 위치
    e_lats = vip_lat + np.random.uniform(-0.003, 0.003, 3)
    e_lons = vip_lon + np.random.uniform(-0.003, 0.003, 3)
    
    df_map = pd.DataFrame({
        '위도': np.concatenate([[vip_lat], p_lats, e_lats]),
        '경도': np.concatenate([[vip_lon], p_lons, e_lons]),
        '구분': ['VIP 차량'] + [f'파파라치 {i+1}' for i in range(paparazzi_count)] + [f'경호팀 {i+1}' for i in range(3)],
        '위험도': [100] + list(np.random.randint(60, 95, paparazzi_count)) + [10]*3,
        '크기': [25] + [15]*paparazzi_count + [18]*3
    })
    
    fig = px.scatter_mapbox(
        df_map,
        lat="위도",
        lon="경도",
        color="구분",
        size="크기",
        hover_name="구분",
        color_discrete_map={
            'VIP 차량': '#00FF66',
            '경호팀 1': '#00BFFF', '경호팀 2': '#00BFFF', '경호팀 3': '#00BFFF',
        },
        zoom=14,
        height=420
    )
    
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin={"r":0, "t":0, "l":0, "b":0},
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 긴급 현장 액션 버튼
    act_col1, act_col2, act_col3 = st.columns(3)
    with act_col1:
        if st.button("🚨 경호팀 긴급 사이렌 작동"):
            st.warning("경호 차량 경고음 발상 및 도로 우선 확보 요청을 완료했습니다!")
    with act_col2:
        if st.button("💨 플래시 교란탄 연막 스위치"):
            st.success("차량 후방 교란 플래시 발사! 파파라치 시야가 5초간 차단됩니다.")
    with act_col3:
        if st.button("📞 112 경찰 긴급 출동 신고"):
            st.error("관할 경찰서에 스토킹 및 과속 위협 행위로 신고 접수되었습니다.")

with right_col:
    st.subheader("🛡️ AI 위기 대응 및 대피 가이드")
    
    tab1, tab2 = st.tabs(["🛣️ AI 탈출 경로 추천", "📝 언론 대응 긴급 성명서"])
    
    with tab1:
        st.write("현재 도로 상황 및 파파라치 분포도를 기반으로 최적 대피 경로를 산출합니다.")
        
        prompt_route = f"연예인 {vip_name}이(가) 현재 파파라치 차량 {paparazzi_count}대에 둘러싸여 쫓기고 있습니다. 위협 수준은 {threat_level}입니다. 연예인이 파파라치를 따돌리고 안전하게 피신할 수 있는 3가지 긴급 대피 전략(예: 지하 주차장 이용, 백화점 내부 이동, 매니저 차량 교대 등)을 신속하게 불렛포인트로 제시해주세요."
        
        if st.button("🤖 AI 탈출 경로 실시간 생성"):
            if ai_enabled:
                with st.spinner("AI가 파파라치 회피 경로 분석 중..."):
                    try:
                        response = model.generate_content(prompt_route)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"AI 응답 생성 중 오류 발생: {e}")
            else:
                st.info("💡 [기본 탈출 경로 안]")
                st.markdown("""
                - **1안 (지하주차장 연계)**: 인근 대형 쇼핑몰 B4 지하주차장 진입 후 CCTV 사각지대에서 2호 차량으로 스위치.
                - **2안 (통행 제한 구역 활용)**: 일반 차량 출입이 제한된 호텔 VIP 전용 승하차장(Drop-off Zone)으로 즉시 진입.
                - **3안 (경호팀 분산 유도)**: 경호 Alpha팀이 1차선에서 파파라치 시선을 분산시키는 동안 VIP 차량은 골목길 우회.
                """)
                
    with tab2:
        st.write("파파라치 추격 과정에서 일어난 소동에 대해 소속사의 공식 입장을 신속히 작성합니다.")
        media_context = st.text_input("추가 상황 입력", value="과속 추적 중 파파라치 카메라 플래시로 인한 운전 방해")
        
        if st.button("📄 긴급 성명서 자동 작성"):
            prompt_statement = f"연예인 {vip_name}의 소속사 명의로 공식 입장문을 작성해줘. 상황: 파파라치의 무리한 추격({media_context})으로 인해 아티스트의 안전이 심각하게 위협받았음. 과도한 사생활 침해에 대한 강력한 법적 대응 및 팬들에게 안심을 전하는 고품격 경고문을 300자 내외로 작성해줘."
            
            if ai_enabled:
                with st.spinner("공식 입장문 작성 중..."):
                    try:
                        response = model.generate_content(prompt_statement)
                        st.success("작성 완료!")
                        st.text_area("공식 입장문 복사용", value=response.text, height=200)
                    except Exception as e:
                        st.error(f"성명서 생성 중 오류 발생: {e}")
            else:
                st.success("작성 완료! (기본 템플릿)")
                template = f"안녕하세요, {vip_name} 소속사입니다.\n\n금일 발생한 무분별한 파파라치 추격 행위로 인해 아티스트의 신변 및 도로 교통 안전에 심각한 위협이 가해졌습니다. 당사는 아티스트의 사생활 보호와 안전 확보를 위해 위법 행위에 대하여 어떠한 합의 없이 강력한 법적 조치를 취할 예정입니다.\n\n걱정해 주신 팬 여러분께 감사드리며, 아티스트의 안전에 최선을 다하겠습니다."
                st.text_area("공식 입장문 복사용", value=template, height=200)

# -----------------------------------------------------------------------------
# 6. 하단 실시간 경호 기록 로그 (Streamlit 기본 구성요소)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📋 실시간 경호 상황 로그 (Live Logs)")

log_data = [
    {"시간": "14:02:11", "내용": f"VIP [{vip_name}] 차량 이동 개시 (강남구 청담동 일대)", "상태": "정상"},
    {"시간": "14:03:45", "내용": f"미식별 검은색 SUV 등 파파라치 차량 {paparazzi_count}대 포착", "상태": "경고"},
    {"시간": "14:04:10", "내용": "경호팀 1차 차단선 구축 및 속도 조절", "상태": "대응중"},
    {"시간": "14:05:00", "내용": "AI 최적 회피 경로 산출 완료 및 관제센터 전달", "상태": "완료"}
]

st.dataframe(pd.DataFrame(log_data), use_container_width=True)
