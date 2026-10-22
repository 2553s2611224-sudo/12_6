
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="SHIELD | 연예인 경호 관제",
    page_icon="🛡️",
    layout="wide",
)

KST = ZoneInfo("Asia/Seoul")

# -----------------------------
# 디자인
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

.stApp {
    background: #0b1018;
    color: #edf4fc;
    font-family: 'Noto Sans KR', sans-serif;
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
}
section[data-testid="stSidebar"] {
    background: #111b28;
}
.hero {
    background: linear-gradient(120deg, #192b43, #101925);
    border: 1px solid #2a3b50;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 22px;
}
.hero h1 {
    color: #f4f8ff;
    font-size: 2.2rem;
    margin: 8px 0;
}
.eyebrow {
    color: #6fe4c2;
    letter-spacing: 3px;
    font-size: 12px;
    font-weight: bold;
}
.muted {
    color: #98abc1;
}
.metric {
    background: #111b28;
    border: 1px solid #29394d;
    border-radius: 15px;
    padding: 18px;
    min-height: 115px;
}
.metric-label {
    color: #9bacc0;
    font-size: 13px;
}
.metric-value {
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
    color: #f2f7fc;
}
.panel {
    background: #111b28;
    border: 1px solid #29394d;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
}
.status-safe { color: #6fe4c2; font-weight: bold; }
.status-warn { color: #ffd782; font-weight: bold; }
.status-danger { color: #ff9292; font-weight: bold; }
div.stButton > button {
    border-radius: 10px;
    min-height: 43px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 시뮬레이션 데이터
# -----------------------------
SCENARIOS = [
    {
        "status": "안정",
        "risk": 22,
        "risk_label": "낮음",
        "location": "A 출입구 · 비공개 행사장",
        "summary": "이동 동선이 확보되어 있고 경호팀이 대기 중입니다.",
        "action": "현재 동선을 유지하고 출입구 주변 상황을 관찰하세요.",
        "event": "경호팀이 이동 동선을 확인했습니다.",
    },
    {
        "status": "주의",
        "risk": 54,
        "risk_label": "보통",
        "location": "B 대기 구역 · 비공개 행사장",
        "summary": "출입구 주변 취재 인원이 증가한 상황입니다.",
        "action": "대체 출입구를 확인하고 현장 책임자와 이동 시점을 조율하세요.",
        "event": "현장 인원 증가에 따라 동선 재확인이 필요합니다.",
    },
    {
        "status": "경계",
        "risk": 81,
        "risk_label": "높음",
        "location": "C 차량 승하차 구역",
        "summary": "이동 경로가 혼잡하여 안전 확인이 필요한 상황입니다.",
        "action": "이동을 잠시 보류하고 경호 책임자와 상황을 확인하세요.",
        "event": "안전 확인 전까지 이동을 보류하도록 권고합니다.",
    },
]

if "scenario_index" not in st.session_state:
    st.session_state.scenario_index = 0

if "events" not in st.session_state:
    st.session_state.events = [
        {
            "time": "14:02:11",
            "level": "안내",
            "message": "경호팀 사전 브리핑 완료",
        },
        {
            "time": "14:04:26",
            "level": "주의",
            "message": "출입구 주변 인원 확인",
        },
        {
            "time": "14:05:03",
            "level": "안전",
            "message": "대기 차량 확인 완료",
        },
    ]

if "emergency" not in st.session_state:
    st.session_state.emergency = False

if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now(KST)

scenario = SCENARIOS[st.session_state.scenario_index]

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.markdown("## 🛡️ SHIELD")
    st.caption("CELEBRITY PROTECTION SYSTEM")
    st.divider()

    st.markdown("### 작전 정보")
    celebrity = st.text_input("보호 대상", "아티스트 A")
    mission = st.selectbox(
        "작전 유형",
        ["행사장 이동", "공항 이동", "퇴근 동선", "비공개 일정"],
    )
    guards = st.selectbox(
        "배치 경호 인원",
        [2, 3, 4, 5, 6, 8],
        index=2,
    )
    show_events = st.toggle("상황 로그 표시", value=True)

    st.divider()
    st.caption("시뮬레이션 모드 · 실제 센서와 연결되지 않음")

# -----------------------------
# 상단 헤더
# -----------------------------
now = datetime.now(KST)

st.markdown(f"""
<div class="hero">
    <div class="eyebrow">SHIELD / PROTECTION OPERATIONS</div>
    <h1>실시간 경호 상황 관제</h1>
    <div class="muted">
        {celebrity or "보호 대상 미지정"} · {mission}
        · 경호 인원 {guards}명
        · {now.strftime("%Y-%m-%d %H:%M:%S")} KST
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 상태 카드
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">현재 경호 상태</div>
        <div class="metric-value">{scenario["status"]}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">시뮬레이션 위험도</div>
        <div class="metric-value">{scenario["risk"]}/100</div>
        <div class="muted">위험도: {scenario["risk_label"]}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">배치 경호 인원</div>
        <div class="metric-value">{guards}명</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">마지막 업데이트</div>
        <div class="metric-value" style="font-size:21px">
            {st.session_state.last_update.strftime("%H:%M:%S")}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

left, right = st.columns([1.15, 0.85], gap="large")

# -----------------------------
# 현장 상황 및 이동 동선
# -----------------------------
with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📍 현장 상황")
    st.markdown(f"### {scenario['location']}")
    st.write(scenario["summary"])

    st.progress(
        scenario["risk"] / 100,
        text=f"위험도 참고 지표 · {scenario['risk']}/100",
    )
    st.caption("위험도는 시연을 위한 예시이며 실제 위험을 판정하지 않습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🧭 이동 동선 체크")

    route = [
        ("1", "집결 지점", "경호팀 인원 확인"),
        ("2", "보안 통로", "주변 혼잡도 확인"),
        ("3", "전용 차량", "차량 확인 및 안전 승차"),
        ("4", "안전 목적지", "도착 후 인원 확인"),
    ]

    for number, title, description in route:
        st.markdown(
            f"**{number}. {title}**  \n"
            f"<span style='color:#98abc1'>{description}</span>",
            unsafe_allow_html=True,
        )
        st.write("")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 경호팀 및 권장 대응
# -----------------------------
with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("⚡ 권장 대응")
    st.write(scenario["action"])

    if scenario["risk"] >= 80:
        st.error("경계 단계: 이동 전 안전 확인이 필요합니다.")
    elif scenario["risk"] >= 50:
        st.warning("주의 단계: 대체 동선을 검토하세요.")
    else:
        st.success("안정 단계: 현재 상황을 계속 관찰하세요.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("👥 경호팀 상태")

    team_status = [
        ("팀장 / 무전", "연결"),
        ("근접 경호", "대기"),
        ("동선 확인", "확인 중" if scenario["risk"] >= 50 else "정상"),
        ("차량 담당", "대기"),
    ]

    for role, status in team_status:
        st.markdown(f"**{role}**")
        st.caption(f"상태: {status}")
        st.divider()

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 관제 버튼
# -----------------------------
st.subheader("🎛️ 관제 액션")

b1, b2, b3 = st.columns(3)

with b1:
    if st.button("🔄 상황 업데이트", use_container_width=True):
        st.session_state.scenario_index = (
            st.session_state.scenario_index + 1
        ) % len(SCENARIOS)

        updated = SCENARIOS[st.session_state.scenario_index]
        st.session_state.events.insert(
            0,
            {
                "time": datetime.now(KST).strftime("%H:%M:%S"),
                "level": updated["status"],
                "message": updated["event"],
            },
        )
        st.session_state.events = st.session_state.events[:10]
        st.session_state.last_update = datetime.now(KST)
        st.rerun()

with b2:
    if st.button("📝 상황 보고 기록", use_container_width=True):
        st.session_state.events.insert(
            0,
            {
                "time": datetime.now(KST).strftime("%H:%M:%S"),
                "level": "기록",
                "message": (
                    f"{celebrity or '보호 대상 미지정'} · {mission} · "
                    f"위험도 {scenario['risk']}/100 · 경호 인원 {guards}명"
                ),
            },
        )
        st.session_state.events = st.session_state.events[:10]
        st.session_state.last_update = datetime.now(KST)
        st.success("상황 보고가 이벤트 로그에 기록되었습니다.")

with b3:
    if st.button("🚨 비상 상황 선언", type="primary", use_container_width=True):
        st.session_state.emergency = True
        st.session_state.events.insert(
            0,
            {
                "time": datetime.now(KST).strftime("%H:%M:%S"),
                "level": "비상",
                "message": "시연용 비상 상황이 선언되었습니다.",
            },
        )
        st.session_state.events = st.session_state.events[:10]
        st.session_state.last_update = datetime.now(KST)

if st.session_state.emergency:
    st.error(
        "비상 상태 활성화 — 이 기능은 화면 내 시뮬레이션이며 "
        "경호팀이나 긴급 구조기관에 연락하지 않습니다."
    )
    if st.button("비상 상태 해제"):
        st.session_state.emergency = False
        st.rerun()

# -----------------------------
# 이벤트 로그
# -----------------------------
st.divider()
st.subheader("📋 최근 상황 이벤트")

if show_events:
    for event in st.session_state.events:
        with st.container(border=True):
            st.caption(
                f"{event['time']} · {event['level']}"
            )
            st.write(event["message"])
else:
    st.info("상황 로그 표시가 꺼져 있습니다.")

st.caption(
    "SHIELD DEMO · 실제 GPS, 카메라 감지, 자동 추적, "
    "외부 경호팀 통신 기능은 포함되어 있지 않습니다."
)
