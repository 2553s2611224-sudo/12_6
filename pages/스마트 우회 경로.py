import streamlit as st
import datetime

# 1. 페이지 테마 기본 설정
st.set_page_config(
    page_title="시크릿 가이드 - 파파라치 위협 우회 도우미",
    page_icon="🛡️",
    layout="centered"
)

# 2. 상단 브랜딩 및 안내 문구
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🛡️ 파팔치 가이드 (Secret Space)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold; color: #4B5563;'>당신의 사생활과 안전을 지키기 위한 위험 우회 도우미</p>", unsafe_allow_html=True)

st.info("💡 **혼자 해결하기 어려운 상황이라면 도움을 요청하세요.**")

# 긴급 공지 박스
st.error("""
**🚨 지금 즉시 위험한 상황인가요?**
누군가 미행하거나, 프라이빗 존을 침범하여 즉각적인 위협이 있다면 앱에 기록하기보다 안전한 공공장소로 이동하고 즉시 **112**에 신고하세요.
""")

with st.expander("📌 긴급 상황 시 필수 행동 요령"):
    st.write("1. **증거 확보:** 카메라 셔터음이 들렸거나 카메라 렌즈를 발견했다면 해당 방향을 조용히 기록하세요.")
    st.write("2. **우회로 확보:** 사전에 등록된 제휴 보안 지역이나 대형 관공서 건물의 내부로 이동하세요.")
    st.write("3. **개인정보 보호:** 이름, 차량번호, 거주지 주소가 노출되지 않도록 동선을 즉시 변경하세요.")

st.markdown("---")

# 3. 탭 구성 (기능별 화면 분할)
tab1, tab2, tab3 = st.tabs(["📝 위협 진단 및 신고서", "🧭 실시간 안전 우회 가이드", "📂 내 보안 기록"])

# ==============================================================================
# TAB 1: 위협 진단 및 사생활 침해 신고서 작성
# ==============================================================================
with tab1:
    st.subheader("📋 사생활 침해 및 파파라치 피해 신고서")
    st.caption("아는 범위에서 작성하세요. 개인 식별이 가능한 민감정보는 입력하지 마세요.")
    
    with st.form("paparazzi_report_form", clear_on_submit=False):
        
        # Q1. 피해 유형
        injury_type = st.radio(
            "⚠️ 어떤 피해를 겪고 있나요?",
            ["동의 없는 촬영 (몰래카메라 등)", "상습적인 미행 및 스토킹", "사생활 정보 온라인 유포", "핫스팟 구역 내 무단 대기 인원 위협"]
        )
        
        # Q2. 발생 장소
        location_type = st.selectbox(
            "📍 주로 어디에서 발생했거나 목격하셨나요?",
            ["오프라인 (현장 / 특정 빌딩 주차장 및 후문)", "온라인 (SNS / 커뮤니티)", "주거지 및 프라이빗 존 인근", "기타 공공장소"]
        )
        
        # Q3. 지속 여부
        is_continuing = st.radio(
            "⏳ 현재도 위협이 계속되고 있나요?",
            ["예, 현재 진행형으로 계속되고 있음", "아니요, 현재는 멈춤/이동함", "잘 모르겠음"]
        )
        
        # Q4. 상황 심각도
        severity = st.select_slider(
            "🚨 현재 상황의 위협 수준은 어떤가요?",
            options=["일반적인 피해 기록", "반복되어 불안하거나 위협을 느낌", "즉각적인 신체/정신적 위험이 있음"]
        )
        
        # Q5. 상세 경위
        details = st.text_area(
            "📝 어떤 일이 있었나요? 구체적인 정황을 적어주세요.",
            placeholder="예: 특정 건물 출입구에서 대기 중인 파파라치를 식별했고, 우회 경로를 찾았으나 지속적으로 동선을 쫓아오는 느낌을 받았습니다."
        )
        
        # Q6. 요구 사항
        need_help = st.multiselect(
            "🤝 어떤 도움이 필요하신가요? (중복 선택 가능)",
            ["실시간 안전 우회 경로 안내", "제휴 보안팀 현장 출동 요청", "증거 자료 채증 및 법적 대응 안내", "온라인 게시물 삭제 지원"]
        )
        
        st.markdown("---")
        
        # 필수 동의 체크박스
        agreement = st.checkbox("이 앱은 공식 사법기관이 아니며, 작성 내용이 경찰에 자동 전달되지 않는다는 점을 확인했습니다.")
        
        submit_button = st.form_submit_button("🛡️ 보안 진단 결과 생성 및 기록")
        
        if submit_button:
            if not agreement:
                st.error("❌ 필수 확인 사항에 동의하셔야 진단 결과를 확인할 수 있습니다.")
            else:
                st.success("✅ 위협 분석이 완료되었습니다! '내 보안 기록' 탭과 아래 가이드를 확인하세요.")
                # 임시 세션 상태에 저장하여 다른 탭에서 볼 수 있게 조치
                st.session_state['latest_report'] = {
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": injury_type,
                    "location": location_type,
                    "status": is_continuing,
                    "level": severity,
                    "desc": details if details else "내용 없음"
                }

# ==============================================================================
# TAB 2: 실시간 안전 우회 가이드
# ==============================================================================
with tab2:
    st.subheader("🧭 실시간 핫스팟 우회 시스템")
    st.caption("현재 제보 데이터를 기반으로 위험 지역을 자동으로 필터링하여 안전한 대체 동선을 제안합니다.")
    
    st.markdown("### 🚨 현재 실시간 탐지된 위험 구역 (레드존)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.error("**[🔥 심각] 강남역 10번출구 이면도로**\n- 파파라치 3개 팀 대기 중\n- 우회 반경: 200m 권장")
        st.warning("**[⚠️ 경고] 신논현역 인근 카페 골목**\n- 기습 촬영 및 인파 밀집 제보 접수\n- 우회 반경: 100m 권장")
    with col_b:
        st.error("**[🔥 심각] 역삼동 프라이빗 빌딩 주차장**\n- 차량 번호판 표적 촬영 주의\n- 우회 반경: 150m 권장")
        st.info("**[ℹ️ 주의] 교보타워 후문 대기선**\n- 단순 인파 급증으로 진입 정체")

    st.markdown("---")
    st.markdown("### 🔒 내비게이션 목적지별 보안 우회 경로")
    
    destination = st.selectbox(
        "목적지를 선택하시면 파파라치를 피하는 최적의 우회로를 안내합니다.",
        ["선택 안함", "안전 가옥 A (강남파이낸스 인근)", "비공개 스튜디오 B (논현동 방향)", "VIP 피신처 C (교대역 방향)"]
    )
    
    if destination == "안전 가옥 A (강남파이낸스 인근)":
        st.success("🎯 **우회 경로 최적화 완료 (안전도 98%)**")
        st.markdown("""
        - **기존 직진 경로:** 강남역 10번 출구 통과 **(위험: 파파라치 노출 확률 높음)**
        - **🔄 보안 우회 경로:** 강남역 1번 출구 방향 국기원 사거리 이면도로로 크게 선회 ➡️ 테헤란로 골목길 진입 ➡️ 지하 주차장 3층 화물 엘리베이터 동선 이용
        - **현장 아군 지원:** `🛡️ 알파가드 B팀`이 해당 동선 입구에서 거점 근무 중입니다.
        """)
    elif destination == "비공개 스튜디오 B (논현동 방향)":
        st.success("🎯 **우회 경로 최적화 완료 (안전도 92%)**")
        st.markdown("""
        - **기존 직진 경로:** 신논현역 메인 카페 거리 통과 **(위험: 인파 밀집 및 기습 촬영 위험)**
        - **🔄 보안 우회 경로:** 사평대로 교보타워 사거리에서 우회전 ➡️ 반포동 주거지역 이면도로 무정차 통과 ➡️ 학동로 방면으로 우회 진입
        - **현장 아군 지원:** 위험 징후 발견 시 즉시 내부 거점 대피소로 진입하십시오.
        """)
    elif destination == "VIP 피신처 C (교대역 방향)":
        st.success("🎯 **우회 경로 최적화 완료 (안전도 95%)**")
        st.markdown("""
        - **기존 직진 경로:** 서초대로 중심가 직선 이동
        - **🔄 보안 우회 경로:** 효령로 방면 외곽 도로 이용 ➡️ 법원단지 뒷길 보안 게이트로 진입
        - **특이사항:** 해당 구역은 파파라치 청정 구역입니다. 안심하고 이동하셔도 좋습니다.
        """)
    else:
        st.info("💡 위에서 안전하게 이동하고자 하는 목적지를 선택해 주세요.")

# ==============================================================================
# TAB 3: 내 기록 확인 및 보관
# ==============================================================================
with tab3:
    st.subheader("📂 저장된 보안 위협 기록")
    
    if 'latest_report' in st.session_state:
        rep = st.session_state['latest_report']
        
        st.markdown(f"""
        <div style='border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; background-color: #F9FAFB;'>
            <span style='background-color: #EF4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;'>{rep['level']}</span>
            <p style='margin-top: 10px; color: #6B7280; font-size: 13px;'>⏳ 기록 일시: {rep['time']}</p>
            <h4 style='margin: 5px 0; color: #111827;'>피해 유형: {rep['type']}</h4>
            <p style='color: #374151;'><b>발생 장소 종류:</b> {rep['location']}</p>
            <p style='color: #374151;'><b>현재 상태:</b> {rep['status']}</p>
            <hr style='margin: 10px 0; border: 0.5px solid #E5E7EB;'>
            <p style='color: #4B5563; font-style: italic;'><b>상세 경위 기록내용:</b><br>"{rep['desc']}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ 기록 데이터 파기 (보안 삭제)"):
            del st.session_state['latest_report']
            st.rerun()
    else:
        st.text("현재 기록된 사생활 침해 및 위협 제보 내용이 없습니다.")
        st.caption("첫 번째 탭에서 신고서를 작성하고 버튼을 누르면 이곳에 암호화된 세션 기록이 남습니다.")

# 4. 하단 카피라이트 및 보호 문구
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 11px; color: #9CA3AF;'>© Secret Space. 본 앱의 모든 데이터는 브라우저 세션 내에만 임시 보관되며 서버에 수집되지 않습니다.</p>", unsafe_allow_html=True)
