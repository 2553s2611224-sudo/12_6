

import streamlit as st
from datetime import datetime
from uuid import uuid4
import csv
import io

st.set_page_config(
    page_title="SAFE SPACE | 사생활 침해 신고",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- 디자인 ----------
st.markdown("""
<style>
.stApp {
    background: #f5f7fb;
}
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    background: linear-gradient(135deg, #172554, #1d4ed8);
    color: white;
    padding: 30px 26px;
    border-radius: 20px;
    margin-bottom: 20px;
}
.hero h1 {
    font-size: 2.2rem;
    margin-bottom: 8px;
}
.hero p {
    color: #e0e7ff;
    margin-bottom: 0;
}
.notice {
    background: #fff7ed;
    border-left: 5px solid #f97316;
    padding: 15px;
    border-radius: 8px;
    margin: 12px 0;
}
.safe-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    margin-bottom: 10px;
}
div.stButton > button {
    border-radius: 10px;
    min-height: 44px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------- 세션 초기화 ----------
if "reports" not in st.session_state:
    st.session_state.reports = []

if "last_report_id" not in st.session_state:
    st.session_state.last_report_id = None


def safe_text(value, default="미입력"):
    """예상하지 못한 빈 값에 대비한다."""
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def build_report_text(report):
    """신고 내용을 텍스트 파일용 문자열로 변환한다."""
    fields = [
        ("신고 번호", report["id"]),
        ("접수 기록 시각", report["created_at"]),
        ("피해 유형", report["category"]),
        ("발생 장소", report["location"]),
        ("지속 여부", report["ongoing"]),
        ("위험 수준", report["risk"]),
        ("상황 설명", report["description"]),
        ("요청 사항", report["request"]),
    ]
    return "\n".join(f"{key}: {value}" for key, value in fields)


# ---------- 상단 ----------
st.markdown("""
<div class="hero">
    <h1>🛡️ SAFE SPACE</h1>
    <p>당신의 사생활과 안전을 지키기 위한 신고 도우미</p>
    <p>혼자 해결하기 어려운 상황이라면 도움을 요청하세요.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
<strong>🚨 지금 위험한 상황인가요?</strong><br>
누군가 위협하거나 따라오거나, 즉각적인 신체적 위험이 있다면
앱에 기록하기보다 안전한 장소로 이동하고 112에 신고하세요.
</div>
""", unsafe_allow_html=True)

# ---------- 긴급 신고 ----------
st.subheader("🚨 긴급 도움")

left, right = st.columns(2)

with left:
    st.link_button(
        "📞 112 긴급신고",
        "tel:112",
        type="primary",
        use_container_width=True,
    )

with right:
    st.link_button(
        "🌐 경찰청 홈페이지",
        "https://www.police.go.kr/",
        use_container_width=True,
    )

st.caption(
    "전화 버튼은 기기의 전화 기능 지원 여부에 따라 작동합니다. "
    "이 앱은 경찰에 신고를 자동 접수하거나 위치를 전송하지 않습니다."
)

with st.expander("긴급 상황에서 기억할 것"):
    st.markdown("""
    1. 가능하면 사람이 있는 안전한 장소로 이동하세요.
    2. 위협하는 사람과 직접 대치하지 마세요.
    3. 112에 현재 위치와 위험 상황을 전달하세요.
    4. 미성년자라면 믿을 수 있는 보호자, 교사 등에게도 알리세요.
    5. 앱에 신고서를 작성하느라 긴급 연락을 늦추지 마세요.
    """)

st.divider()

# ---------- 메뉴 ----------
tab_report, tab_records, tab_guide = st.tabs([
    "📝 신고서 작성",
    "📂 내 기록",
    "🧭 안전 가이드",
])

# ---------- 신고서 작성 ----------
with tab_report:
    st.subheader("사생활 침해 신고서")
    st.write(
        "아는 범위에서 작성하세요. 이름, 집 주소, 비밀번호, "
        "주민등록번호 등 불필요한 민감정보는 입력하지 마세요."
    )

    with st.form("report_form", clear_on_submit=False):
        category = st.selectbox(
            "어떤 피해를 겪고 있나요?",
            [
                "몰래 촬영 또는 촬영물 유포",
                "개인정보 또는 신상정보 공개",
                "반복적인 연락 또는 따라다님",
                "계정 무단 접근 또는 사칭",
                "대화·사진 무단 공유",
                "기타 사생활 침해",
            ],
        )

        location = st.selectbox(
            "주로 어디에서 발생했나요?",
            [
                "온라인 / SNS",
                "학교 / 학원",
                "집 주변 / 이동 중",
                "공공장소",
                "직장 / 기타 실내",
                "기타 / 밝히고 싶지 않음",
            ],
        )

        ongoing = st.radio(
            "현재도 계속되고 있나요?",
            ["예, 계속되고 있음", "아니요, 현재는 멈춤", "잘 모르겠음"],
            horizontal=False,
        )

        risk = st.radio(
            "현재 상황은 어떤가요?",
            [
                "일반적인 피해 기록",
                "반복되어 불안하거나 위협을 느낌",
                "즉각적인 위험이 있음",
            ],
        )

        description = st.text_area(
            "어떤 일이 있었나요?",
            placeholder=(
                "예: 동의 없이 사진이 공유되었고, "
                "삭제를 요청했지만 다시 게시되었습니다."
            ),
            max_chars=2000,
            height=140,
        )

        request = st.selectbox(
            "어떤 도움이 필요한가요?",
            [
                "대응 방법 안내",
                "보호자 또는 학교에 알릴 준비",
                "경찰 등 공식 기관에 상담 또는 신고",
                "증거 정리 방법 안내",
                "기타 도움",
            ],
        )

        confirm = st.checkbox(
            "이 앱은 공식 신고기관이 아니며, "
            "작성 내용이 경찰에 자동 전달되지 않는다는 점을 확인했습니다."
        )

        submitted = st.form_submit_button(
            "신고 내용 기록하기",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not description.strip():
            st.error("상황 설명을 한 줄 이상 작성해 주세요.")
        elif not confirm:
            st.warning("안내 내용을 확인한 뒤 체크해 주세요.")
        else:
            report = {
                "id": uuid4().hex[:8].upper(),
                "created_at": datetime.now().astimezone().strftime(
                    "%Y-%m-%d %H:%M:%S %Z"
                ),
                "category": category,
                "location": location,
                "ongoing": ongoing,
                "risk": risk,
                "description": description.strip(),
                "request": request,
            }

            st.session_state.reports.append(report)
            st.session_state.last_report_id = report["id"]

            st.success(
                f"기록이 완료되었습니다. 기록 번호: {report['id']}"
            )

            if risk == "즉각적인 위험이 있음":
                st.error(
                    "즉각적인 위험이 있다고 선택했습니다. "
                    "지금 위험하다면 기록보다 안전 확보와 112 신고를 먼저 하세요."
                )
            elif ongoing == "예, 계속되고 있음":
                st.warning(
                    "피해가 지속되고 있다면 믿을 수 있는 사람에게 알리고, "
                    "필요하면 경찰 등 공식 기관에 도움을 요청하세요."
                )

            st.info(
                "이 기록은 현재 브라우저 세션에만 보관됩니다. "
                "공식 기관에 전송된 신고가 아닙니다."
            )

# ---------- 내 기록 ----------
with tab_records:
    st.subheader("📂 내가 작성한 기록")

    reports = st.session_state.reports

    if not reports:
        st.info("아직 기록이 없습니다. '신고서 작성'에서 기록할 수 있어요.")
    else:
        st.write(f"현재 세션의 기록: **{len(reports)}건**")

        for report in reversed(reports):
            with st.expander(
                f"{report['created_at']} · {report['category']} · "
                f"번호 {report['id']}"
            ):
                st.markdown(build_report_text(report))

                st.download_button(
                    "⬇️ 이 기록 다운로드",
                    data=build_report_text(report),
                    file_name=f"safe_space_{report['id']}.txt",
                    mime="text/plain",
                    key=f"download_{report['id']}",
                    use_container_width=True,
                )

        st.divider()
        st.markdown("**모든 기록을 CSV로 다운로드**")

        csv_buffer = io.StringIO()
        columns = [
            "id", "created_at", "category", "location",
            "ongoing", "risk", "description", "request"
        ]
        writer = csv.DictWriter(
            csv_buffer,
            fieldnames=columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(reports)

        st.download_button(
            "📥 전체 기록 CSV 다운로드",
            data="\ufeff" + csv_buffer.getvalue(),
            file_name="safe_space_reports.csv",
            mime="text/csv",
            use_container_width=True,
        )

        if st.button("🗑️ 현재 세션의 모든 기록 삭제", type="secondary"):
            st.session_state.reports = []
            st.session_state.last_report_id = None
            st.rerun()

# ---------- 안전 가이드 ----------
with tab_guide:
    st.subheader("🧭 상황별 안전 가이드")

    with st.expander("📷 몰래 촬영 또는 사진 유포"):
        st.markdown("""
        - 게시물 주소, 계정명, 날짜 등 필요한 정보를 안전하게 기록하세요.
        - 플랫폼의 신고 및 삭제 요청 기능을 이용할 수 있습니다.
        - 불법 촬영물이나 사적인 사진을 다른 사람에게 재전송하지 마세요.
        - 유포 협박이나 추가 피해가 있다면 경찰에 도움을 요청하세요.
        """)

    with st.expander("📱 반복적인 연락 또는 따라다님"):
        st.markdown("""
        - 혼자 만나거나 직접 대치하지 마세요.
        - 안전한 장소로 이동하고 믿을 수 있는 사람에게 알리세요.
        - 연락 기록 등 관련 자료를 안전하게 보존하세요.
        - 즉각적인 위험이 있으면 112에 신고하세요.
        """)

    with st.expander("🔐 개인정보 유출 또는 계정 침해"):
        st.markdown("""
        - 안전한 기기에서 비밀번호를 변경하고 2단계 인증을 설정하세요.
        - 다른 계정에서도 같은 비밀번호를 사용했다면 함께 변경하세요.
        - 로그인 기록과 플랫폼 신고 내역을 보존하세요.
        - 금융 피해나 계정 도용이 있다면 해당 기관에도 연락하세요.
        """)

    with st.expander("🏫 학교에서 발생한 사생활 침해"):
        st.markdown("""
        - 믿을 수 있는 교사, 상담교사 또는 보호자에게 알리세요.
        - 피해가 반복되면 날짜와 상황을 간단히 정리하세요.
        - 보복이나 위협이 우려되면 혼자 해결하려 하지 마세요.
        """)

    st.markdown("### 📌 도움을 요청할 곳")
    st.markdown("""
    - **112** — 경찰 긴급신고
    - **117** — 학교폭력 신고·상담
    - **1366** — 여성긴급전화
    """)

    st.caption(
        "연락처는 서비스별 이용 대상과 운영 범위가 다를 수 있습니다. "
        "즉각적인 위험은 112에 연락하세요."
    )

# ---------- 하단 안내 ----------
st.divider()
st.caption(
    "SAFE SPACE는 사생활 침해 피해 기록과 안전 정보 제공을 위한 "
    "시범 앱입니다. 공식 신고 접수, 수사, 위치 추적 기능은 제공하지 않습니다."
)
st.caption(
    "개인정보 보호 안내: 기본 버전은 외부 데이터베이스에 기록을 "
    "저장하지 않습니다. 다운로드한 파일은 사용자가 직접 관리해야 합니다."
)
