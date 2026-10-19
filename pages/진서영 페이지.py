import sqlite3
from datetime import date, datetime, time
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "risk_records.db"

st.set_page_config(
    page_title="SAFELOG | 위험 상황 기록 관리",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme and visual styling
st.markdown(
    """
    <style>
      .stApp { background: #f5f7fb; }
      [data-testid="stSidebar"] { background: #111827; }
      [data-testid="stSidebar"] * { color: #f9fafb !important; }
      .hero {
        padding: 1.35rem 1.5rem; border-radius: 18px;
        background: linear-gradient(120deg, #111827 0%, #26364f 70%, #36506b 100%);
        color: white; margin-bottom: 1rem;
      }
      .hero h1 { margin: 0 0 .35rem 0; font-size: 2rem; }
      .hero p { margin: 0; color: #dbeafe; }
      .small-note { color: #64748b; font-size: .9rem; }
      div[data-testid="stMetric"] {
        background: white; border: 1px solid #e5eaf2;
        padding: 1rem; border-radius: 14px;
      }
      div[data-testid="stForm"] {
        background: white; border: 1px solid #e5eaf2;
        padding: 1rem; border-radius: 14px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def connect_db():
    """Open the local SQLite database and ensure the table exists."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_date TEXT NOT NULL,
                incident_time TEXT NOT NULL,
                location TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                subject_alias TEXT,
                person_description TEXT,
                vehicle_description TEXT,
                summary TEXT NOT NULL,
                action_taken TEXT,
                reporter TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        return conn
    except sqlite3.Error as exc:
        st.error(f"데이터베이스를 열 수 없습니다: {exc}")
        st.stop()


def load_records():
    try:
        conn = connect_db()
        df = pd.read_sql_query(
            "SELECT * FROM incidents ORDER BY incident_date DESC, incident_time DESC, id DESC",
            conn,
        )
        conn.close()
        return df
    except (sqlite3.Error, pd.errors.DatabaseError) as exc:
        st.error(f"기록을 불러오지 못했습니다: {exc}")
        return pd.DataFrame()


def save_record(values):
    conn = connect_db()
    try:
        conn.execute(
            """
            INSERT INTO incidents (
                incident_date, incident_time, location, incident_type, severity,
                subject_alias, person_description, vehicle_description, summary,
                action_taken, reporter, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["incident_date"].isoformat(),
                values["incident_time"].strftime("%H:%M"),
                values["location"].strip(),
                values["incident_type"],
                values["severity"],
                values["subject_alias"].strip(),
                values["person_description"].strip(),
                values["vehicle_description"].strip(),
                values["summary"].strip(),
                values["action_taken"].strip(),
                values["reporter"].strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_record(record_id):
    conn = connect_db()
    try:
        conn.execute("DELETE FROM incidents WHERE id = ?", (int(record_id),))
        conn.commit()
    finally:
        conn.close()


def show_header(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def safe_text(value):
    if pd.isna(value) or str(value).strip() == "":
        return "미기록"
    return str(value)


# Initialize DB before rendering pages.
_ = connect_db()

with st.sidebar:
    st.markdown("## 🛡️ SAFELOG")
    st.caption("위험 상황 기록 · 관리")
    page = st.radio(
        "메뉴",
        ["대시보드", "위험 상황 등록", "기록 조회", "위험 지역 분석"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**기록 원칙**")
    st.caption("사건 대응을 위한 최소한의 정보만 기록하세요.")
    st.caption("실제 인물의 집 주소, 실시간 이동 경로 등 민감한 정보는 입력하지 마세요.")
    st.caption("이 앱은 기록 관리 도구이며 긴급 신고를 대신하지 않습니다.")

records = load_records()

if page == "대시보드":
    show_header("위험 상황 기록 센터", "촬영·미행 등 위험 상황을 정리하고 반복되는 위험 신호를 확인합니다.")
    today = date.today().isoformat()
    total = len(records)
    recent = int((records["incident_date"] == today).sum()) if total else 0
    high = int(records["severity"].isin(["높음", "긴급"]).sum()) if total else 0
    places = int(records["location"].nunique()) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 기록", f"{total}건")
    c2.metric("오늘 발생", f"{recent}건")
    c3.metric("높음 · 긴급", f"{high}건")
    c4.metric("기록된 장소", f"{places}곳")

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("최근 위험 상황")
        if records.empty:
            st.info("아직 기록이 없습니다. ‘위험 상황 등록’ 메뉴에서 첫 기록을 추가하세요.")
        else:
            recent_df = records.head(6).copy()
            recent_df["발생 일시"] = recent_df["incident_date"] + " " + recent_df["incident_time"]
            recent_df = recent_df.rename(
                columns={"location": "장소", "incident_type": "유형", "severity": "위험도", "summary": "상황 요약"}
            )
            st.dataframe(
                recent_df[["발생 일시", "장소", "유형", "위험도", "상황 요약"]],
                use_container_width=True,
                hide_index=True,
            )
    with right:
        st.subheader("기록 분포")
        if records.empty:
            st.markdown(
                """
                <div style="background:white;border:1px solid #e5eaf2;border-radius:14px;padding:1rem;">
                <b>이 화면에서 확인할 수 있어요</b><br><br>
                • 날짜별 사건 기록<br>
                • 촬영·미행 유형별 빈도<br>
                • 반복 신고가 접수된 장소<br>
                • 위험도별 기록 현황
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            type_counts = records["incident_type"].value_counts().rename_axis("유형").reset_index(name="건수")
            st.bar_chart(type_counts.set_index("유형"))
            severity_counts = records["severity"].value_counts().rename_axis("위험도").reset_index(name="건수")
            st.caption("위험도별 기록")
            st.dataframe(severity_counts, use_container_width=True, hide_index=True)

    st.divider()
    st.caption("개인 프로젝트용 기본 버전입니다. Streamlit Community Cloud의 로컬 파일은 영구 보관용 저장소가 아닐 수 있으므로 중요한 기록은 정기적으로 CSV로 내보내 보관하세요.")

elif page == "위험 상황 등록":
    show_header("위험 상황 등록", "기억이 선명할 때 시간·장소·상황을 객관적으로 기록하세요.")
    st.info("안전이 우선입니다. 위험이 계속되면 안전한 장소로 이동하고 소속사 보안 담당자 또는 경찰 등 적절한 기관에 도움을 요청하세요. 긴급 상황은 112에 신고하세요.")

    with st.form("incident_form", clear_on_submit=True):
        st.subheader("1. 발생 정보")
        col1, col2, col3 = st.columns(3)
        with col1:
            incident_date = st.date_input("발생 날짜", value=date.today(), max_value=date.today())
        with col2:
            incident_time = st.time_input("발생 시간", value=datetime.now().time().replace(second=0, microsecond=0))
        with col3:
            incident_type = st.selectbox(
                "상황 유형",
                ["무단 촬영", "도보 미행", "차량 추적 의심", "주거·숙소 주변 대기", "위협·접근", "온라인 정보 노출", "기타"],
            )
        col4, col5 = st.columns(2)
        with col4:
            location = st.text_input("장소 또는 구역 *", placeholder="예: 행사장 출입구 주변 / ○○역 인근")
        with col5:
            severity = st.select_slider("위험도", options=["낮음", "보통", "높음", "긴급"], value="보통")

        st.subheader("2. 관찰한 특징")
        col6, col7 = st.columns(2)
        with col6:
            person_description = st.text_area(
                "촬영자·접근 인물의 관찰 가능한 특징",
                placeholder="예: 검은색 모자, 회색 상의, 카메라 소지",
                height=100,
            )
        with col7:
            vehicle_description = st.text_area(
                "차량 특징 (해당 시)",
                placeholder="예: 어두운 색 SUV, 차종 추정은 불확실함",
                height=100,
            )
        subject_alias = st.text_input("관련 대상 별칭 (선택)", placeholder="예: 행사 A / 이동 B")
        summary = st.text_area(
            "상황 요약 *",
            placeholder="무슨 일이 있었는지 관찰한 사실 위주로 작성하세요. 추측은 추측이라고 표시하세요.",
            height=130,
        )
        action_taken = st.text_area(
            "대응 및 후속 조치",
            placeholder="예: 경호 담당자에게 전달, 안전한 장소로 이동, 신고 접수",
            height=90,
        )
        reporter = st.text_input("기록자 (선택)", placeholder="예: 담당자 이니셜")

        submitted = st.form_submit_button("기록 저장", type="primary", use_container_width=True)
        if submitted:
            if not location.strip() or not summary.strip():
                st.error("‘장소 또는 구역’과 ‘상황 요약’은 꼭 입력해 주세요.")
            else:
                try:
                    save_record(
                        {
                            "incident_date": incident_date,
                            "incident_time": incident_time,
                            "location": location,
                            "incident_type": incident_type,
                            "severity": severity,
                            "subject_alias": subject_alias,
                            "person_description": person_description,
                            "vehicle_description": vehicle_description,
                            "summary": summary,
                            "action_taken": action_taken,
                            "reporter": reporter,
                        }
                    )
                    st.success("위험 상황 기록을 저장했습니다.")
                    st.rerun()
                except (sqlite3.Error, ValueError, OSError) as exc:
                    st.error(f"저장에 실패했습니다. 입력 내용을 확인하고 다시 시도해 주세요. ({exc})")

elif page == "기록 조회":
    show_header("기록 조회", "날짜·유형·위험도 조건으로 이전 사례를 찾아봅니다.")
    if records.empty:
        st.info("조회할 기록이 없습니다. 먼저 위험 상황을 등록해 주세요.")
    else:
        min_date = pd.to_datetime(records["incident_date"]).min().date()
        max_date = pd.to_datetime(records["incident_date"]).max().date()
        f1, f2, f3 = st.columns(3)
        with f1:
            start_date = st.date_input("시작 날짜", value=min_date, key="search_start")
        with f2:
            end_date = st.date_input("종료 날짜", value=max_date, key="search_end")
        with f3:
            search_text = st.text_input("장소·요약 검색", placeholder="검색어 입력")

        f4, f5 = st.columns(2)
        with f4:
            type_options = ["전체"] + sorted(records["incident_type"].dropna().unique().tolist())
            selected_type = st.selectbox("상황 유형", type_options)
        with f5:
            severity_options = ["전체", "낮음", "보통", "높음", "긴급"]
            selected_severity = st.selectbox("위험도", severity_options)

        if start_date > end_date:
            st.warning("시작 날짜는 종료 날짜보다 늦을 수 없습니다.")
        else:
            filtered = records[
                (records["incident_date"] >= start_date.isoformat())
                & (records["incident_date"] <= end_date.isoformat())
            ].copy()
            if selected_type != "전체":
                filtered = filtered[filtered["incident_type"] == selected_type]
            if selected_severity != "전체":
                filtered = filtered[filtered["severity"] == selected_severity]
            if search_text.strip():
                mask = (
                    filtered["location"].fillna("").str.contains(search_text, case=False, regex=False)
                    | filtered["summary"].fillna("").str.contains(search_text, case=False, regex=False)
                    | filtered["person_description"].fillna("").str.contains(search_text, case=False, regex=False)
                    | filtered["vehicle_description"].fillna("").str.contains(search_text, case=False, regex=False)
                )
                filtered = filtered[mask]

            st.caption(f"검색 결과: {len(filtered)}건")
            display = filtered.copy()
            display["발생 일시"] = display["incident_date"] + " " + display["incident_time"]
            display = display.rename(
                columns={
                    "id": "번호",
                    "location": "장소",
                    "incident_type": "유형",
                    "severity": "위험도",
                    "summary": "상황 요약",
                    "action_taken": "대응",
                }
            )
            cols = ["번호", "발생 일시", "장소", "유형", "위험도", "상황 요약", "대응"]
            st.dataframe(display[cols], use_container_width=True, hide_index=True)

            st.subheader("기록 상세 보기")
            ids = filtered["id"].astype(int).tolist()
            if ids:
                chosen_id = st.selectbox("상세 내용을 볼 기록 번호", ids, format_func=lambda x: f"기록 #{x}")
                chosen = filtered[filtered["id"] == chosen_id].iloc[0]
                with st.expander("선택한 기록의 상세 내용", expanded=True):
                    st.write(f"**발생 일시:** {chosen['incident_date']} {chosen['incident_time']}")
                    st.write(f"**장소:** {safe_text(chosen['location'])}")
                    st.write(f"**유형 / 위험도:** {chosen['incident_type']} / {chosen['severity']}")
                    st.write(f"**관련 대상 별칭:** {safe_text(chosen['subject_alias'])}")
                    st.write(f"**인물 특징:** {safe_text(chosen['person_description'])}")
                    st.write(f"**차량 특징:** {safe_text(chosen['vehicle_description'])}")
                    st.write(f"**상황 요약:** {safe_text(chosen['summary'])}")
                    st.write(f"**대응:** {safe_text(chosen['action_taken'])}")
                    st.write(f"**기록자:** {safe_text(chosen['reporter'])}")
                    with st.popover("이 기록 삭제"):
                        st.warning("삭제한 기록은 복구할 수 없습니다.")
                        confirm = st.checkbox("삭제할 기록 번호와 내용을 확인했습니다.")
                        if st.button("영구 삭제", type="primary", disabled=not confirm):
                            try:
                                delete_record(chosen_id)
                                st.success("기록을 삭제했습니다.")
                                st.rerun()
                            except sqlite3.Error as exc:
                                st.error(f"삭제에 실패했습니다: {exc}")

            csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "검색 결과 CSV 다운로드",
                data=csv_bytes,
                file_name=f"risk_records_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

elif page == "위험 지역 분석":
    show_header("위험 지역 분석", "누적 기록에서 반복적으로 등장하는 장소와 상황 유형을 확인합니다.")
    if records.empty:
        st.info("분석할 기록이 없습니다. 기록이 쌓이면 이 화면에 통계가 표시됩니다.")
    else:
        counts = records.groupby("location", dropna=False).size().sort_values(ascending=False)
        top_n = min(10, len(counts))
        top_places = counts.head(top_n).rename_axis("장소").reset_index(name="기록 건수")
        a, b = st.columns([1.2, 1])
        with a:
            st.subheader("반복 기록 장소 TOP 10")
            st.bar_chart(top_places.set_index("장소"))
            st.dataframe(top_places, use_container_width=True, hide_index=True)
        with b:
            st.subheader("유형별 분포")
            type_counts = records["incident_type"].value_counts().rename_axis("유형").reset_index(name="건수")
            st.bar_chart(type_counts.set_index("유형"))
            st.subheader("위험도 분포")
            sev_counts = records["severity"].value_counts().reindex(
                ["긴급", "높음", "보통", "낮음"], fill_value=0
            ).rename_axis("위험도").reset_index(name="건수")
            st.dataframe(sev_counts, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("기간별 추이")
        daily = records.groupby("incident_date").size().rename("기록 건수").to_frame()
        st.line_chart(daily)
        st.caption("주의: 이 통계는 입력된 기록만을 집계합니다. 특정 장소의 위험성을 확정하거나 개인의 행동을 추적하는 자료로 사용하지 마세요.")
        st.download_button(
            "전체 기록 CSV 다운로드",
            data=records.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"all_risk_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

st.markdown("---")
st.markdown(
    '<p class="small-note">SAFELOG · 기록은 사실 중심으로 작성하고, 민감한 개인 정보는 최소화하세요.</p>',
    unsafe_allow_html=True,
)
