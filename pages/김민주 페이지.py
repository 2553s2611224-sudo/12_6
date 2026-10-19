
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="PRISM | 경호 관제",
    page_icon="🛡️",
    layout="wide",
)

# ---------- 화면 디자인 ----------
st.markdown("""
<style>
.stApp {
    background: #0b1020;
    color: #eef2ff;
}
[data-testid="stSidebar"] {
    background: #11182b;
}
[data-testid="stMetric"] {
    background: #141d32;
    border: 1px solid #273653;
    padding: 14px;
    border-radius: 14px;
}
.panel {
    background: #121a2d;
    border: 1px solid #273653;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}
.hero {
    background: linear-gradient(120deg, #17233e, #121a2d);
    border: 1px solid #2b3b5c;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 20px;
}
.muted {
    color: #9eacc8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ---------- 초기 데이터 ----------
def initialize():
    defaults = {
        "risk": "주의",
        "phase": "이동 중",
        "zone": "가상 구역 B-04",
        "alerts": [],
        "incident_count": 0,
        "team": {
            "팀장 A-01": "대기",
            "근접 경호 A-02": "동행 중",
            "차량 담당 V-01": "차량 대기",
            "현장 확인 S-01": "주변 확인",
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_alert(level, message, action="상황판 조작"):
    st.session_state.alerts.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "message": message,
        "action": action,
    })
    st.session_state.alerts = st.session_state.alerts[:100]


def risk_icon(risk):
    return {
        "안전": "🟢",
        "주의": "🟡",
        "경계": "🟠",
        "위험": "🔴",
    }.get(risk, "⚪")


def show_alerts(items):
    if not items:
        st.info("아직 등록된 경보가 없습니다.")
        return

    for item in items:
        st.markdown(
            f"""
            <div class="panel">
                <strong>{risk_icon(item['level'])}
                {item['level']} · {item['message']}</strong>
                <p class="muted">
                {item['time']} · 조치: {item['action']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


initialize()

# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown("## 🛡️ PRISM")
    st.caption("CELEBRITY PROTECTION CONSOLE")
    st.divider()

    page = st.radio(
        "관제 메뉴",
        [
            "실시간 상황판",
            "경호팀 관리",
            "사건·경보 기록",
            "운영 안내",
        ],
    )

    st.divider()
    st.success("시뮬레이션 모드")
    st.caption("실제 위치 데이터는 사용하지 않습니다.")

# ---------- 상단 제목 ----------
st.markdown("""
<div class="hero">
    <div class="muted">PRISM / PROTECTION OPERATIONS</div>
    <h1>연예인 경호 관제 센터</h1>
    <p>파파라치 접근 상황을 가정한 경호 대응 시뮬레이션</p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 1. 실시간 상황판
# ==================================================
if page == "실시간 상황판":

    active_count = sum(
        status != "대기"
        for status in st.session_state.team.values()
    )
    alert_count = sum(
        item["level"] != "INFO"
        for item in st.session_state.alerts
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "현재 위험도",
        f"{risk_icon(st.session_state.risk)} {st.session_state.risk}",
    )
    c2.metric(
        "경호팀 가동",
        f"{active_count} / {len(st.session_state.team)}명",
    )
    c3.metric("누적 경보", f"{alert_count}건")
    c4.metric("등록 사건", f"{st.session_state.incident_count}건")

    left, right = st.columns([1.2, 0.8])

    with left:
        st.subheader("현재 상황")

        st.markdown(
            f"""
            <div class="panel">
                <h3>{risk_icon(st.session_state.risk)}
                {st.session_state.risk} 단계</h3>
                <p>상황: <strong>{st.session_state.phase}</strong></p>
                <p>위치: <strong>{st.session_state.zone}</strong></p>
                <p class="muted">
                가상 구역이며 실제 주소가 아닙니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("상황 업데이트")

        phases = [
            "이동 준비",
            "이동 중",
            "주변 인원 접근",
            "차량 탑승",
            "안전 장소 대기",
        ]
        risks = ["안전", "주의", "경계", "위험"]
        zones = [
            "가상 구역 A-01",
            "가상 구역 B-04",
            "가상 구역 C-02",
            "가상 안전 장소 Z-01",
        ]

        phase = st.selectbox(
            "상황 단계",
            phases,
            index=phases.index(st.session_state.phase)
            if st.session_state.phase in phases else 1,
        )
        risk = st.selectbox(
            "위험도",
            risks,
            index=risks.index(st.session_state.risk),
        )
        zone = st.selectbox(
            "가상 구역",
            zones,
            index=zones.index(st.session_state.zone)
            if st.session_state.zone in zones else 1,
        )

        if st.button("상황 업데이트", type="primary",
                     use_container_width=True):
            st.session_state.phase = phase
            st.session_state.risk = risk
            st.session_state.zone = zone
            add_alert(
                risk if risk != "안전" else "INFO",
                f"상황 업데이트: {phase} / {risk}",
                "관제 담당자 업데이트",
            )
            st.rerun()

        st.subheader("빠른 대응")

        b1, b2, b3 = st.columns(3)

        if b1.button("🔎 주변 확인", use_container_width=True):
            st.session_state.team["현장 확인 S-01"] = "주변 확인"
            add_alert("주의", "현장 주변 확인 요청")
            st.rerun()

        if b2.button("🛡️ 경호 강화", use_container_width=True):
            st.session_state.risk = "경계"
            st.session_state.team["팀장 A-01"] = "대응 지휘"
            st.session_state.team["근접 경호 A-02"] = "경호 강화"
            add_alert(
                "경계",
                "경호 강화 단계로 전환",
                "경호 인력 재배치",
            )
            st.rerun()

        if b3.button("🚐 안전 대기", use_container_width=True):
            st.session_state.phase = "안전 장소 대기"
            st.session_state.zone = "가상 안전 장소 Z-01"
            add_alert("주의", "안전 장소 대기 상태로 전환")
            st.rerun()

    with right:
        st.subheader("경호팀 현황")

        for name, status in st.session_state.team.items():
            st.markdown(
                f"""
                <div class="panel">
                    <strong>{name}</strong>
                    <p>{status}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("최근 경보")
        show_alerts(st.session_state.alerts[:3])


# ==================================================
# 2. 경호팀 관리
# ==================================================
elif page == "경호팀 관리":

    st.subheader("경호 인력 상태 관리")
    st.caption("상태는 현재 앱 세션에서만 유지됩니다.")

    statuses = [
        "대기",
        "동행 중",
        "주변 확인",
        "차량 대기",
        "경호 강화",
        "대응 지휘",
    ]

    for name, current in list(st.session_state.team.items()):
        with st.container(border=True):
            col1, col2 = st.columns([1, 1])
            col1.write(f"**{name}**")

            selected = col2.selectbox(
                f"{name} 상태",
                statuses,
                index=statuses.index(current)
                if current in statuses else 0,
                key=f"status_{name}",
                label_visibility="collapsed",
            )

            if selected != current:
                st.session_state.team[name] = selected
                add_alert(
                    "INFO",
                    f"{name} 상태 변경: {selected}",
                    "경호팀 관리",
                )
                st.rerun()

    st.divider()
    st.subheader("안전 점검 체크리스트")

    st.checkbox("경호팀 간 연락 상태 확인")
    st.checkbox("차량 및 출입 동선 확인")
    st.checkbox("불필요한 위치 정보 공유 중단")
    st.checkbox("안전 장소 담당자와 연락 확인")


# ==================================================
# 3. 사건 및 경보 기록
# ==================================================
elif page == "사건·경보 기록":

    st.subheader("사건 및 경보 이력")

    selected_levels = st.multiselect(
        "표시할 단계",
        ["INFO", "주의", "경계", "위험"],
        default=["INFO", "주의", "경계", "위험"],
    )

    filtered = [
        item for item in st.session_state.alerts
        if item["level"] in selected_levels
    ]
    show_alerts(filtered)

    st.divider()
    st.subheader("새 사건 등록")

    with st.form("incident_form", clear_on_submit=True):
        incident_type = st.selectbox(
            "사건 유형",
            [
                "파파라치로 의심되는 접근",
                "촬영 시도 목격",
                "이동 동선 노출 우려",
                "현장 혼잡",
                "기타 안전 우려",
            ],
        )
        severity = st.selectbox(
            "위험도",
            ["주의", "경계", "위험"],
        )
        note = st.text_area(
            "메모",
            placeholder="확인된 사실만 간단히 기록하세요.",
            max_chars=500,
        )
        submitted = st.form_submit_button(
            "사건 등록",
            type="primary",
        )

        if submitted:
            message = incident_type
            if note.strip():
                message += " — " + note.strip()

            st.session_state.incident_count += 1
            add_alert(severity, message, "사건 기록 등록")
            st.success("사건을 등록했습니다.")
            st.rerun()

    if st.button("기록 초기화"):
        st.session_state.alerts = []
        st.session_state.incident_count = 0
        add_alert("INFO", "기록 초기화 완료")
        st.rerun()


# ==================================================
# 4. 운영 안내
# ==================================================
elif page == "운영 안내":

    st.subheader("앱 사용 방법")

    st.markdown("""
    **이 앱은 가상 경호 훈련용 프로토타입입니다.**

    - **실시간 상황판:** 위험도와 상황 단계를 바꿔 보세요.
    - **경호팀 관리:** 경호 인력의 가상 상태를 수정하세요.
    - **사건·경보 기록:** 사건을 등록하고 이력을 확인하세요.
    - **데이터 저장:** 데이터는 앱 세션 메모리에만 저장됩니다.
      세션 종료나 재시작 시 사라질 수 있습니다.
    - **실제 연동 없음:** GPS, CCTV, 카메라 감지,
      문자 발송, 외부 경호 시스템과 연결되지 않습니다.
    - **개인정보 보호:** 실제 인물의 위치나 사적인 일정,
      확인되지 않은 혐의 내용을 입력하지 마세요.

    실제 운영에 사용하려면 인증, 접근 권한 관리,
    안전한 데이터 저장 및 개인정보 보호 검토가 필요합니다.
    """)

st.divider()
st.caption(
    "PRISM · Demonstration only · 가상 데이터 기반 경호 시뮬레이션"
)

