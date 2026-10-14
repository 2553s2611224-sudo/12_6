import streamlit as st
import pandas as pd
from datetime import datetime
import os
import google.generativeai as genai

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="VIP Security Radar - 파파라치 감지 & 경호 알림",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "alerts" not in st.session_state:
    st.session_state.alerts = [
        {
            "id": 1,
            "time": "2026-10-14 14:10",
            "artist": "VIP A (배우)",
            "location": "강남구 청담동 미용실 앞",
            "threat_type": "비인가 대형 카메라 촬영",
            "level": "보통 (Medium)",
            "status": "대응 중",
            "description": "검은색 카니발 차량 뒤에서 파파라치 2명이 망원 렌즈로 지속 촬영 중."
        },
        {
            "id": 2,
            "time": "2026-10-14 13:45",
            "artist": "VIP B (아이돌)",
            "location": "김포공항 입구",
            "threat_type": "사생팬 및 사설 파파라치 추적",
            "level": "높음 (High)",
            "status": "조치 완료",
            "description": "차량 이동 경로를 오토바이 2대가 미행함. B경호팀에 의해 따돌림 완료."
        }
    ]

# ---------------------------------------------------------
# Gemini API Setup (Optional Helper)
# ---------------------------------------------------------
def analyze_threat_with_gemini(description):
    """Gemini API를 활용한 위협 상황 분석 및 경호 지침 생성"""
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    
    if not api_key:
        return "⚠️ Secrets에 GEMINI_API_KEY가 설정되어 있지 않아 기본 분석을 제공합니다.\n\n[기본 지침] 즉시 해당 지역을 이탈하고 VIP를 안전지대로 이동시키세요."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = f"""
        당신은 전문 연예인 경호 팀장입니다.
        아래 파파라치/추적 상황을 바탕으로 위험도 평가(낮음, 보통, 높음, 심각)와 경호팀이 즉시 취해야 할 행동 지침 3가지를 요약해서 작성해 주세요.

        상황 설명:
        {description}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ API 호출 중 오류가 발생했습니다: {str(e)}"

# ---------------------------------------------------------
# UI & Header
# ---------------------------------------------------------
st.title("🛡️ VIP Security Radar: 파파라치 감지 및 실시간 경호 알림")
st.caption("연예인 및 VIP 대상 파파라치, 사생팬, 추적 상황을 실시간 감지하여 경호팀에 공유하는 모니터링 시스템")

# Sidebar - Quick SOS Button & Menu
st.sidebar.header("🚨 긴급 SOS 신호 발생")
with st.sidebar.form("sos_form"):
    sos_artist = st.selectbox("VIP 선택", ["VIP A (배우)", "VIP B (아이돌)", "VIP C (가수)"])
    sos_location = st.text_input("현재 위치", value="성수동 카페거리 인근")
    sos_threat = st.selectbox("위협 종류", ["파파라치 밀착 촬영", "추적 차량 감지", "사생팬 인파 밀집", "드론 촬영 감지"])
    sos_desc = st.text_area("상황 설명", value="모자를 쓴 남성이 10분째 근처에서 몰래 촬영하고 있습니다.")
    
    submit_sos = st.form_submit_button("🚨 즉시 SOS 발령")
    
    if submit_sos:
        new_alert = {
            "id": len(st.session_state.alerts) + 1,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "artist": sos_artist,
            "location": sos_location,
            "threat_type": sos_threat,
            "level": "심각 (Critical)",
            "status": "접수됨",
            "description": sos_desc
        }
        st.session_state.alerts.insert(0, new_alert)
        st.sidebar.success("🚨 SOS 경보가 경호팀 전원에 전송되었습니다!")

# ---------------------------------------------------------
# Main Tabs
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📡 실시간 모니터링", "📝 위협 제보 등록", "🤖 AI 위협 분석기"])

# Tab 1: Live Monitoring
with tab1:
    st.subheader("📊 실시간 위협 감지 현황")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("총 감지 건수", len(st.session_state.alerts))
    active_count = sum(1 for a in st.session_state.alerts if a["status"] != "조치 완료")
    col2.metric("현재 대응 중", f"{active_count} 건", delta_color="inverse")
    col3.metric("시스템 상태", "NORMAL (정상 운용 중)")
    
    st.divider()
    
    # Table / Cards Display
    for idx, alert in enumerate(st.session_state.alerts):
        status_color = "🔴" if alert["status"] == "접수됨" else ("🟡" if alert["status"] == "대응 중" else "🟢")
        
        with st.expander(f"{status_color} [{alert['time']}] {alert['artist']} - {alert['threat_type']} ({alert['location']})", expanded=(idx==0)):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**위험 수준:** {alert['level']}")
                st.write(f"**상세 내용:** {alert['description']}")
            with col_b:
                new_status = st.selectbox(
                    "상태 변경",
                    ["접수됨", "대응 중", "조치 완료"],
                    index=["접수됨", "대응 중", "조치 완료"].index(alert["status"]),
                    key=f"status_{alert['id']}"
                )
                if new_status != alert["status"]:
                    st.session_state.alerts[idx]["status"] = new_status
                    st.rerun()

# Tab 2: Report Threat
with tab2:
    st.subheader("✍️ 파파라치 / 미행 상황 수동 등록")
    with st.form("manual_report_form"):
        r_artist = st.selectbox("대상 아티스트", ["VIP A (배우)", "VIP B (아이돌)", "VIP C (가수)"])
        r_location = st.text_input("위치", placeholder="예: 한남동 UN빌리지 정문 앞")
        r_threat = st.selectbox("위협 감지 유형", ["비인가 대형 카메라 촬영", "미행 오토바이/차량", "사생팬 집결", "기타 사생활 침해"])
        r_level = st.select_slider("위험 정도", options=["낮음 (Low)", "보통 (Medium)", "높음 (High)", "심각 (Critical)"])
        r_desc = st.text_area("상황 설명 및 특이사항")
        
        submit_report = st.form_submit_button("제보 제출")
        if submit_report:
            if not r_location or not r_desc:
                st.warning("위치와 상황 설명을 입력해 주세요.")
            else:
                st.session_state.alerts.insert(0, {
                    "id": len(st.session_state.alerts) + 1,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "artist": r_artist,
                    "location": r_location,
                    "threat_type": r_threat,
                    "level": r_level,
                    "status": "접수됨",
                    "description": r_desc
                })
                st.success("제보가 정상적으로 접수되었습니다.")
                st.rerun()

# Tab 3: AI Threat Analysis
with tab3:
    st.subheader("🤖 AI 기반 위협 및 대응 전략 분석")
    st.write("파파라치 목격담이나 수집된 정보를 입력하면 AI(Gemini)가 위협을 평가하고 대응 지침을 제공합니다.")
    
    input_text = st.text_area(
        "상황 설명 입력",
        value="공항 주차장에서 검은색 썬팅이 짙은 카니발 차량이 VIP 차량을 지속적으로 미행하고 있으며, 신호 대기 중 창문을 열고 카메라를 밀착하는 행동을 보임.",
        height=100
    )
    
    if st.button("🔍 AI 분석 실행"):
        with st.spinner("Gemini가 위협 요소를 분석 중입니다..."):
            result = analyze_threat_with_gemini(input_text)
            st.markdown("### 📋 분석 및 경호 대응 지침")
            st.info(result)
