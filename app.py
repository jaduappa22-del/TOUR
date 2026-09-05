from datetime import datetime
import json
import pandas as pd
import streamlit as st

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="VOYAGE AI — 스마트 글로벌 여행 인텔리전스",
    page_icon="✈️",
    layout="wide",
)

# 도시별 정보 및 좌표 DB (실시간 환산 계수 및 현지 가이드 포함)
GLOBAL_DESTINATIONS = {
    "도쿄 (일본)": {
        "country": "일본",
        "currency": "JPY",
        "rate": 9.2,  # 100엔당 원화 환산 대략적 계수 (예시)
        "lat": 35.6762,
        "lon": 139.6503,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": (
            "스이카(Suica) 카드 사전 충전 필수, 식당 현금/트래블카드 병행 사용"
        ),
    },
    "파리 (프랑스)": {
        "country": "프랑스",
        "currency": "EUR",
        "rate": 1450.0,
        "lat": 48.8566,
        "lon": 2.3522,
        "emergency": "긴급 통합 콜센터: 112",
        "tips": "소매치기 주의, 지하철 소지품 밀착 관리 필수",
    },
    "뉴욕 (미국)": {
        "country": "미국",
        "currency": "USD",
        "rate": 1350.0,
        "lat": 40.7128,
        "lon": -74.0060,
        "emergency": "긴급 구조: 911",
        "tips": "식당 및 택시 이용 시 15~20% 팁 문화 고려 필수",
    },
    "방콕 (태국)": {
        "country": "태국",
        "currency": "THB",
        "rate": 38.5,
        "lat": 13.7563,
        "lon": 100.5018,
        "emergency": "관광 경찰: 1155",
        "tips": "그랩(Grab) 앱 설치 필수, 사원 방문 시 복장 규정 준수",
    },
}

# 에어비앤비/토스 융합형 하이엔드 감성 CSS
st.markdown("""
    <style>
    .stApp { background-color: #fafafa; color: #111827; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .hero-banner { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 35px; border-radius: 16px; color: white; margin-bottom: 25px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); }
    .card { background-color: #ffffff; padding: 24px; border-radius: 14px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .section-title { font-size: 18px; font-weight: 700; color: #111827; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
    .route-card { background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 14px 18px; border-radius: 8px; margin-bottom: 12px; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
    .badge { background-color: #eff6ff; color: #1d4ed8; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 상단 히어로 배너 (여행 감성 극대화)
st.markdown("""
    <div class="hero-banner">
        <span style="background-color: #3b82f6; color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">AI SMART VOYAGE DESK</span>
        <h1 style="margin: 12px 0 8px 0; font-size: 28px; font-weight: 800;">🌍 실시간 지능형 맞춤 여행 플래너</h1>
        <p style="margin: 0; color: #94a3b8; font-size: 14px;">목적지만 고르면 동선 최적화, 예산 자동 환산, 구글맵 네비게이션 링크까지 완벽하게 설계됩니다.</p>
    </div>
""", unsafe_allow_html=True)

# 사이드바 입력 허브
st.sidebar.markdown(
    "### ✈️ 여행 조건 설정", help="원하시는 목적지와 스타일을 선택하세요."
)
selected_destination = st.sidebar.selectbox(
    "여행지 선택", list(GLOBAL_DESTINATIONS.keys())
)
duration = st.sidebar.selectbox(
    "여행 일정", ["2박 3일", "3박 4일", "4박 5일", "5박 6일"], index=1
)
total_budget_krw = st.sidebar.number_input(
    "총 예산 한도 (원화 기준)", min_value=300000, value=1500000, step=100000
)
travel_style = st.sidebar.multiselect(
    "여행 스타일 및 관심사",
    ["로컬 미식 탐방", "인생샷 랜드마크", "명품/소품 쇼핑", "힐링 스파/카페", "역사/문화 투어"],
    default=["로컬 미식 탐방", "인생샷 랜드마크"],
)

dest_info = GLOBAL_DESTINATIONS[selected_destination]

# 화면 레이아웃 분할
col_left, col_right = st.columns([1.8, 1.2])

with col_left:
  # 1. 일자별 스마트 동선 최적화 플랜
  days_num = int(duration[0])
  st.markdown(
      f'<div class="card"><div class="section-title">🗺️ [{selected_destination}]'
      f" {duration} 동선 최적화 마스터 플랜</div>",
      unsafe_allow_html=True,
  )

  for d in range(1, days_num + 1):
    # 구글맵 검색 연동 링크 생성
    map_query_morning = f"{selected_destination.split(' ')[0]} 랜드마크 추천"
    map_query_lunch = f"{selected_destination.split(' ')[0]} 맛집"
    map_query_night = f"{selected_destination.split(' ')[0]} 야경 명소"

    url_morning = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(map_query_morning)}"
    url_lunch = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(map_query_lunch)}"
    url_night = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(map_query_night)}"

    st.markdown(
        f"""
            <div class="route-card">
                <b>📅 Day {d} 추천 루트 코스</b><br>
                <div style="margin-top: 6px; font-size: 13px; color: #334155;">
                    • <b>오전 스팟</b>: 핵심 랜드마크 및 역사 문화 탐방 [<a href="{url_morning}" target="_blank" style="color: #2563eb; text-decoration: none;">📍 구글맵 길찾기</a>]<br>
                    • <b>오후 미식</b>: 현지인 추천 로컬 맛집 및 카페 투어 [<a href="{url_lunch}" target="_blank" style="color: #2563eb; text-decoration: none;">📍 맛집 위치 보기</a>]<br>
                    • <b>저녁 일정</b>: 야경 감상 및 시그니처 코스 마무으리 [<a href="{url_night}" target="_blank" style="color: #2563eb; text-decoration: none;">📍 야경 스팟 보기</a>]
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 스마트 예산 실시간 역산 및 카테고리 분배
  st.markdown(
      '<div class="card"><div class="section-title">💰 실시간 예산 최적화 및 환산'
      ' 리포트</div>',
      unsafe_allow_html=True,
  )

  # 원화 예산을 현지 통화로 환산
  curr_code = dest_info["currency"]
  rate = dest_info["rate"]

  if curr_code == "JPY":
    local_budget = (total_budget_krw / rate) * 100
    budget_str = f"약 {local_budget:,.0f} 엔 (JPY)"
  elif curr_code == "THB":
    local_budget = total_budget_krw / rate
    budget_str = f"약 {local_budget:,.0f} 밧 (THB)"
  else:
    local_budget = total_budget_krw / rate
    budget_str = f"약 {local_budget:,.2f} {curr_code}"

  col_b1, col_b2 = st.columns(2)
  with col_b1:
    st.metric(label="설정 총 예산 (원화)", value=f"{total_budget_krw:,} 원")
  with col_b2:
    st.metric(label=f"현지 통화 환산 가치 ({curr_code})", value=budget_str)

  budget_breakdown = {
      "지출 항목": ["숙박비 (Hotel)", "식비 및 카페", "교통 패스/이동", "쇼핑 및 비상금"],
      "예상 배정 금액 (원화)": [
          f"{int(total_budget_krw * 0.45):,} 원",
          f"{int(total_budget_krw * 0.30):,} 원",
          f"{int(total_budget_krw * 0.10):,} 원",
          f"{int(total_budget_krw * 0.15):,} 원",
      ],
  }
  st.dataframe(
      pd.DataFrame(budget_breakdown), use_container_width=True, hide_index=True
  )
  st.markdown("</div>", unsafe_allow_html=True)

with col_right:
  # 3. 실시간 지도 레이더 위젯
  st.markdown(
      '<div class="card"><div class="section-title">🛰️ 목적지 거점 레이더 맵</div>',
      unsafe_allow_html=True,
  )
  map_df = pd.DataFrame([{
      "lat": dest_info["lat"],
      "lon": dest_info["lon"],
      "name": selected_destination,
  }])
  st.map(map_df, latitude="lat", longitude="lon", size=400, zoom=11)
  st.markdown("</div>", unsafe_allow_html=True)

  # 4. 현지 비상 연락망 및 필수 팩트체크 팁
  st.markdown(
      '<div class="card"><div class="section-title">🚨 현지 비상 연락망 & 스마트'
      ' 팁</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      f"""
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 12px; border-radius: 8px; margin-bottom: 12px; font-size: 13px; color: #991b1b;">
            <b>📞 현지 긴급 연락처</b><br>{dest_info['emergency']}
        </div>
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 8px; font-size: 13px; color: #166534;">
            <b>💡 스마트 여행 권장 팁</b><br>{dest_info['tips']}
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)
