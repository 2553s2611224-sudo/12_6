import streamlit as st
import random
import google.generativeai as genai

# 1. 페이지 기본 설정 (밝은 테마 및 이모지)
st.set_page_config(
    page_title="파파라치 탈출 작전! 📸",
    page_icon="🏃‍♂️",
    layout="centered"
)

# 2. Gemini API 세팅 및 예외 처리
def get_ai_response(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        return "ERROR: API 키가 설정되지 않았습니다. Secrets를 확인해주세요."
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: AI 연동 중 오류가 발생했습니다. ({str(e)})"

# 3. 세션 상태(Session State) 초기화 (게임 데이터 유지)
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "escape_gauge" not in st.session_state:
    st.session_state.escape_gauge = 30  # 시작 게이지 30%
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "game_log" not in st.session_state:
    st.session_state.game_log = []
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "game_won" not in st.session_state:
    st.session_state.game_won = False

# 게임 리셋 함수
def reset_game():
    st.session_state.game_started = True
    st.session_state.escape_gauge = 30
    st.session_state.game_log = ["🎬 파파라치 추격전이 시작되었습니다! 탈출 게이지를 100%로 만드세요!"]
    st.session_state.game_over = False
    st.session_state.game_won = False
    generate_paparazzi_question()

# 새로운 파파라치 질문 생성 함수
def generate_paparazzi_question():
    scenarios = [
        "열애설 상대와 똑같은 반지를 끼고 있는 것이 포착되었습니다!",
        "방금 고급 레스토랑에서 비밀리에 만나고 나온 사람은 누구인가요?",
        "어제 한밤중에 변장을 하고 마트에 가신 이유가 무엇입니까?",
        "차기작 출연을 거절하셨다는 소문이 도는데 진실을 밝혀주세요!",
        "오늘 공항 패션이 너무 파격적인데, 어떤 심경의 변화가 있나요?"
    ]
    base_scen = random.choice(scenarios)
    prompt = f"너는 집요하지만 유쾌한 연예부 파파라치 기자야. 다음 상황에 대해 스타에게 던질 한 문장의 날카롭고 밝은 톤의 질문을 만들어줘: '{base_scen}'"
    
    with st.spinner("📸 파파라치가 마이크를 들이밀고 있습니다..."):
        ai_q = get_ai_response(prompt)
        if "ERROR" in ai_q:
            st.session_state.current_question = f"📢 [시스템 대체 기습] {base_scen} 해명해주세요!"
        else:
            st.session_state.current_question = ai_q.strip()

# --- 화면 UI 구성 ---

# 타이틀 및 인트로
st.title("🏃‍♂️ 파파라치 탈출 시뮬레이터!")
st.subheader("📸 \"기자님들, 제발 길 좀 비켜주세요~!\"")
st.markdown(
    """
    당신은 전 세계의 주목을 받는 **탑스타**입니다! 
    사방에서 플래시가 터지는 가운데, 센스 있는 답변과 임기응변으로 파파라치들을 따돌리고 
    안전한 대기실 차량(100%)까지 탈출하세요! ✨
    """
)

st.divider()

# 게임 시작 버튼
if not st.session_state.game_started:
    if st.button("🚀 스타의 하루 시작하기 (게임 시작)", type="primary"):
        reset_game()
        st.rerun()

# 게임 진행 화면
if st.session_state.game_started:
    
    # 1. 상태 표시창 (탈출 게이지)
    st.markdown(f"### 🚪 탈출 진행도: **{st.session_state.escape_gauge}%**")
    st.progress(st.session_state.escape_gauge / 100.0)
    
    # 성공/실패 조건 체크
    if st.session_state.escape_gauge >= 100 and not st.session_state.game_won:
        st.session_state.game_won = True
    elif st.session_state.escape_gauge <= 0 and not st.session_state.game_over:
        st.session_state.game_over = False # 아래에서 실패 화면 처리
        
    # 결과 화면 처리
    if st.session_state.game_won:
        st.balloons()
        st.success("🎉 탈출 성공! 안전하게 소속사 밴에 탑승하여 레드카펫으로 이동합니다! 당신은 진정한 프로 탑스타!")
        if st.button("🔄 처음부터 다시 도전하기"):
            reset_game()
            st.rerun()
            
    elif st.session_state.escape_gauge <= 0:
        st.error("📸 탈출 실패... 결국 모든 비밀을 카메라 앞에서 털어놓고 실시간 검색어 1위에 올랐습니다!")
        if st.button("🔄 재도전하기"):
            reset_game()
            st.rerun()
            
    else:
        # 정상 게임 진행 중
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"🎤 **파파라치의 기습 질문:**\n\n\"{st.session_state.current_question}\"")
            
            # 유저 답변 입력 Form
            with st.form(key="answer_form", clear_on_submit=True):
                user_reply = st.text_input("💬 당신의 센스 있는 대답 (변명):", placeholder="예: 아, 그건 제 친척 동생인데요?")
                submit_button = st.form_submit_with_clicks(label="🎤 해명하고 지나가기", input_id="user_reply")
                
                if submit_button and user_reply:
                    # 답변 평가 프롬프트
                    eval_prompt = (
                        f"파파라치 질문: '{st.session_state.current_question}'\n"
                        f"스타의 답변: '{user_reply}'\n"
                        f"이 답변이 얼마나 위트 있고 파파라치를 잘 따돌렸는지 평가해줘. "
                        f"결과는 반드시 '점수: [숫자]' 형태로 첫 줄에 적어줘. 숫자는 답변이 좋으면 10에서 20 사이의 양수, "
                        f"답변이 당황스럽거나 뻔하면 -10에서 -20 사이의 음수로 줘. "
                        f"둘째 줄에는 파파라치들의 유쾌한 반응을 한 줄로 적어줘."
                    )
                    
                    with st.spinner("🎬 기자들의 반응 살피는 중..."):
                        res = get_ai_response(eval_prompt)
                        
                        # 점수 및 파싱 예외처리
                        try:
                            score_line = res.split("\n")[0]
                            score = int(''.join(filter(lambda x: x=='-' or x.isdigit(), score_line)))
                        except:
                            score = random.choice([15, -10]) # 예외 발생 시 랜덤 부여
                        
                        # 게이지 업데이트 및 로그 기록
                        st.session_state.escape_gauge = max(0, min(100, st.session_state.escape_gauge + score))
                        st.session_state.game_log.insert(0, f"💬 나: {user_reply} (게이지 변동: {score}%)")
                        
                        # 다음 질문 세팅
                        generate_paparazzi_question()
                        st.rerun()
        
        with col2:
            st.markdown("⚡ **돌발 상황 회피**")
            # 간단한 즉시 선택형 컴포넌트
            if st.button("🕶️ 선글라스 고쳐쓰기"):
                score = random.choice([5, -5])
                st.session_state.escape_gauge = max(0, min(100, st.session_state.escape_gauge + score))
                st.session_state.game_log.insert(0, f"🕶️ 선글라스를 고쳐써서 분위기를 환기했습니다! ({score}%)")
                st.rerun()
            if st.button("🏃‍♂️ 갑자기 전력 질주"):
                score = random.choice([20, -15])
                st.session_state.escape_gauge = max(0, min(100, st.session_state.escape_gauge + score))
                st.session_state.game_log.insert(0, f"🏃‍♂️ 플래시 세례를 뚫고 뛰었습니다! ({score}%)")
                st.rerun()

        # 실시간 행동 로그 출력
        st.divider()
        st.caption("📜 스타의 실시간 동선 현황")
        for log in st.session_state.game_log[:5]:  # 최근 5개 로그만 출력
            st.write(log)
