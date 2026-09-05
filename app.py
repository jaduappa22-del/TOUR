from datetime import datetime
import json
import pandas as pd
import streamlit as st

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="Global AI Travel Intelligence Desk",
    page_icon="✈️",
    layout="wide",
)

# 도시별 대략적인 중심 좌표 데이터베이스 (동적 지도 시각화용)
CITY_COORDINATES = {
    "도쿄": {"lat": 35.6762, "lon": 139.6503, "country": "일본"},
    "오사카": {"lat": 34.6937, "lon": 135.5022, "country": "일본"},
    "파리": {"lat": 48.8566, "lon": 2.3522, "country": "프랑스"},
    "뉴욕": {"lat": 40.7128, "lon": -74.0060, "country": "미국"},
    "런던": {"lat": 51.5074, "lon": -0.1278, "country": "영국"},
    "방콕": {"lat": 13.7563, "lon": 100.5018, "country": "태국"},
    "싱가포르": {"lat": 1.3521, "lon": 103.8198, "country": "싱가포르"},
    "바르셀로나": {"lat": 41.3851, "lon": 2.1734, "country": "스페인"},
}

# 커스텀 CSS 스타일링
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .main-header { background: linear-gradient(135deg, #0284c7, #0369a1); padding: 25px; border-radius: 12px; color: white; font-weight: 900; font-size: 26px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .card { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .sub-header { font-size: 16px; font-weight: 800; color: #0284c7; margin-bottom: 12px; }
    .itinerary-box { background-color: #f1f5f9; border-left: 4px solid #0284c7; padding: 12px 15px; border-radius: 6px; margin-bottom: 10px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# 상단 헤더
st.markdown("""
    <div class="main-header">
        <span>✈️ GLOBAL AI DYNAMIC TRAVEL INTELLIGENCE DESK</span>
        <span style="font-size: 13px; background-color: #ffffff22; padding: 5px 12px; border-radius: 6px;">MULTI-DESTINATION ENGINE v1.0</span>
    </div>
""", unsafe_allow_html=True)

# 사이드바: 여행 조건 입력 덱
st.sidebar.markdown(
    "### 🧳 맞춤형 여행 조건 설정",
    help="국가와 도시를 자유롭게 입력하면 전용 플랜이 구성됩니다.",
)

input_country = st.sidebar.text_input("국가 입력", value="일본")
input_city = st.sidebar.text_input("도시 입력", value="도쿄")
duration = st.sidebar.selectbox(
    "여행 기간", ["2박 3일", "3박 4일", "4박 5일", "5박 6일"], index=1
)
budget_style = st.sidebar.selectbox(
    "예산 스타일", ["가성비 뚜벅이 (Economy)", "표준 패키지 (Standard)", "프리미엄 럭셔리 (Luxury)"]
)
travel_theme = st.multiselect(
    "핵심 관심사 (복수 선택 가능)",
    ["맛집 탐방", "인생샷/랜드마크", "쇼핑", "휴양/힐링", "역사/문화"],
    default=["맛집 탐방", "쇼핑"],
)

generate_btn = st.sidebar.button(
    "🚀 AI 맞춤형 여행 플랜 생성", use_container_width=True
)

# 메인 콘텐츠 영역
if generate_btn or "itinerary_loaded" not in st.session_state:
  st.session_state.itinerary_loaded = True
  st.session_state.current_city = input_city
  st.session_state.current_country = input_country

# 현재 선택된 도시에 따른 데이터 시뮬레이션
target_city = st.session_state.get("current_city", input_city)
target_country = st.session_state.get("current_country", input_country)

# 도시 좌표 가져오기 (없으면 기본 도쿄 좌표)
coords = CITY_COORDINATES.get(
    target_city, {"lat": 35.6762, "lon": 139.6503, "country": target_country}
)

col_main1, col_main2 = st.columns([2, 1])

with col_main1:
  st.markdown(
      f'<div class="card"><div class="sub-header">📍 [{target_country}'
      f" · {target_city}] {duration} 맞춤형 동선 마스터 플랜</div>",
      unsafe_allow_html=True,
  )

  # 일자별 가상 동선 생성
  days_count = int(duration[0])
  for day in range(1, days_count + 1):
    st.markdown(
        f"""
            <div class="itinerary-box">
                <b>📅 Day {day} 추천 일정 코스</b><br>
                • <b>오전 (09:30 ~ 12:30)</b>: {target_city} 대표 랜드마크 및 역사 문화 스팟 투어<br>
                • <b>오후 (12:30 ~ 18:00)</b>: 현지 로컬 맛집 중식 및 핵심 쇼핑/체험 지구 탐방<br>
                • <b>저녁 (18:00 ~ 21:30)</b>: 야경 명소 감상 및 시그니처 디너 코스 식사
            </div>
        """,
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

  # 예상 예산안 브리프
  st.markdown(
      '<div class="card"><div class="sub-header">💰 예상 소요 예산안 산출'
      ' (1인 기준)</div>',
      unsafe_allow_html=True,
  )

  base_cost = 500000 if "가성비" in budget_style else 1200000
  if "럭셔리" in budget_style:
    base_cost = 2500000

  budget_data = {
      "항목": ["숙박비 (Hotel)", "식비 및 카페", "교통비 (대중교통/택시)", "입장료 및 쇼핑"],
      "예상 비용 (원화 환산)": [
          f"약 {int(base_cost * 0.4):,}원",
          f"약 {int(base_cost * 0.3):,}원",
          f"약 {int(base_cost * 0.1):,}원",
          f"약 {int(base_cost * 0.2):,}원",
      ],
  }
  st.dataframe(
      pd.DataFrame(budget_data), use_container_width=True, hide_index=True
  )
  st.markdown("</div>", unsafe_allow_html=True)

with col_main2:
  # 지도 시각화 위젯
  st.markdown(
      f'<div class="card"><div class="sub-header">🗺️ {target_city} 거점 위치'
      ' 레이더</div>',
      unsafe_allow_html=True,
  )
  map_df = pd.DataFrame(
      [
          {
              "lat": coords["lat"],
              "lon": coords["lon"],
              "name": f"{target_city} 중심가",
          }
      ]
  )
  st.map(map_df, latitude="lat", longitude="lon", size=300, zoom=11)
  st.markdown(
      f'<p style="font-size:12px; color:#64748b; margin-top:8px;">* 선택하신'
      f" <b>{target_country} {target_city}</b>의 핵심 중심 좌표를 기준으로"
      " 렌더링되었습니다.</p>",
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)

  # 실무 팁 & 준비물 카드
  st.markdown(
      '<div class="card"><div class="sub-header">💡 스마트 여행 꿀팁</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      f"1. **현지 통화 및 결제**: {target_country} 여행 시 소액 현금과 트래블"
      " 카드 병행 사용 추천<br>2. **필수 준비물**: 어댑터 규격 확인 및 모바일"
      " 로밍/이심(eSIM) 사전 등록",
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)
