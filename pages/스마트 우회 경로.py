import subprocess
import sys

# 1. ⚡ [한 번에 배포용 핵심 팁] 필요한 지도 라이브러리 자동 설치 처리
try:
    import folium
    from streamlit_folium import st_folium
except ImportError:
    # 라이브러리가 없으면 코드가 실행되면서 자동으로 즉시 설치합니다.
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium==0.15.0", "streamlit-folium==0.15.0"])
    import folium
    from streamlit_folium import st_folium

import streamlit as st
import pandas as pd
import numpy as np

# 2. 페이지 기본 설정 및 스타일
st.set_page_config(
    page_title="시크릿루트 - 파파라치 우회 내비게이션",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ 시크릿루트 (SecretRoute)")
st.caption("파파라치 대기 및 위험 지역을 실시간으로 우회하는 보안 내비게이션 시스템")

# 3. 고정 상태 데이터 (Mock Data) 생성 및 관리
BASE_LAT, BASE_LON = 37.4979, 127.0276

@st.cache_data
def get_mock_data():
    hotspots = pd.DataFrame({
        'NAME': ['강남역 10번출구 앞 (제보 다수)', '신논현역 인근 카페 골목', '역삼동 프라이빗 빌딩 주차장'],
        'LAT': [37.4985, 37.5040, 37.5005],
        'LON': [127.0270, 127.0245, 127.0360],
        'RADIUS':,
        'DANGER_LEVEL': ['심각 (파파라치 3팀 대기)', '경고 (인파 밀집)', '주의 (제보 확인 중)']
    })
    
    security_teams = pd.DataFrame({
        'TEAM': ['캡스 가드 A팀', '에스원 가드 B팀', '자체 경호 C팀'],
        'LAT': [37.4960, 37.5020, 37.4990],
        'LON': [127.0300, 127.0220, 127.0330],
        'STATUS': ['근무 중', '순찰 중', '대기 중']
    })
    
    destinations = {
        "선택 안함": None,
        "안전 가옥 A (강남파이낸스센터 근처)": (37.5015, 127.0365),
        "스튜디오 B (논현동 방향)": (37.5110, 127.0215),
        "비공개 회의실 C (서초동 방향)": (37.4920, 127.0120)
    }
    
    return hotspots, security_teams, destinations

hotspots, security_teams, destinations = get_mock_data()

if 'user_reports' not in st.session_state:
    st.session_state.user_reports = pd.DataFrame(columns=['NAME', 'LAT', 'LON', 'RADIUS', 'DANGER_LEVEL'])

# 4. 레이아웃 분할 (좌측 제어판 / 우측 지도 화면)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📍 내비게이션 설정")
    st.text_input("출발지 (내 위치)", value="현재 위치 (강남역 중심)", disabled=True)
    
    selected_dest_name = st.selectbox("🔒 보안 목적지 설정", list(destinations.keys()))
    target_coords = destinations[selected_dest_name]
    
    st.markdown("---")
    st.subheader("🚨 실시간 파파라치 제보하기")
    with st.form("report_form", clear_on_submit=True):
        report_name = st.text_input("위치 명칭/특이사항", placeholder="예: OO빌딩 후문 진입로")
        submitted = st.form_submit_button("제보 등록")
        
        if submitted:
            if report_name:
                rand_lat = BASE_LAT + np.random.uniform(-0.005, 0.005)
                rand_lon = BASE_LON + np.random.uniform(-0.005, 0.005)
                
                new_report = pd.DataFrame([{
                    'NAME': f"[시민제보] {report_name}",
                    'LAT': rand_lat,
                    'LON': rand_lon,
                    'RADIUS': 130,
                    'DANGER_LEVEL': '확인 중 (최근 제보)'
                }])
                st.session_state.user_reports = pd.concat([st.session_state.user_reports, new_report], ignore_index=True)
                st.success("제보가 실시간으로 반영되었습니다!")
            else:
                st.warning("위치 명칭을 입력해주세요.")

with col2:
    st.subheader("🗺️ 실시간 우회 경로 맵")
    
    try:
        m = folium.Map(location=[BASE_LAT, BASE_LON], zoom_start=14)
        
        # 출발지 마커
        folium.Marker(location=[BASE_LAT, BASE_LON], popup="내 위치", icon=folium.Icon(color="green")).add_to(m)
        
        # 위험 지역 표시
        all_hotspots = pd.concat([hotspots, st.session_state.user_reports], ignore_index=True)
        for _, row in all_hotspots.iterrows():
            folium.Circle(
                location=[row['LAT'], row['LON']], radius=row['RADIUS'],
                color='red', fill=True, fill_color='red', fill_opacity=0.3,
                popup=f"{row['NAME']} ({row['DANGER_LEVEL']})"
            ).add_to(m)
            
        # 제휴 보안팀 표시
        for _, row in security_teams.iterrows():
            folium.Marker(location=[row['LAT'], row['LON']], popup=row['TEAM'], icon=folium.Icon(color="blue", icon="shield")).add_to(m)
            
        # 목적지 설정 시 우회 경로 선 그리기
        if target_coords:
            folium.Marker(location=target_coords, popup=selected_dest_name, icon=folium.Icon(color="black")).add_to(m)
            
            # 가상 우회 알고리즘 구현
            start_point = np.array([BASE_LAT, BASE_LON])
            end_point = np.array(target_coords)
            route_points = [start_point]
            
            for i in range(1, 5):
                mid_point = start_point + (end_point - start_point) * (i / 5)
                for _, room in all_hotspots.iterrows():
                    center = np.array([room['LAT'], room['LON']])
                    if np.linalg.norm(mid_point - center) < 0.003:
                        mid_point = center + ((mid_point - center) / (np.linalg.norm(mid_point - center) + 1e-6)) * 0.0035
                route_points.append(mid_point)
            route_points.append(end_point)
            
            folium.PolyLine(route_points, color="blue", weight=5, opacity=0.7).add_to(m)
            st.success(f"🔒 {selected_dest_name}까지 안전 우회 경로가 생성되었습니다.")
        else:
            st.info("목적지를 지정하시면 실시간 우회 경로가 계산됩니다.")

        st_folium(m, width="100%", height=500)
        
    except Exception as e:
        st.error(f"지도 렌더링 중 오류 발생: {e}")

st.markdown("---")
st.dataframe(all_hotspots[['NAME', 'DANGER_LEVEL', 'RADIUS']], use_container_width=True)
