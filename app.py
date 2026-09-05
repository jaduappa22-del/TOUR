from datetime import datetime
import json
import urllib.parse
import pandas as pd
import streamlit as st

# 페이지 설정 (와이드 모드)
st.set_page_config(
    page_title="VOYAGE AI — 프리미엄 글로벌 인텔리전스 플래너",
    page_icon="✈️",
    layout="wide",
)

# 글로벌 도시 확장 DB (오키나와, 상하이, 타이페이, 오사카 포함)
GLOBAL_DESTINATIONS = {
    "도쿄 (일본)": {
        "country": "일본",
        "currency": "JPY",
        "rate": 9.2,
        "lat": 35.6762,
        "lon": 139.6503,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "스이카(Suica) 카드 사전 충전 필수, 식당 현금/트래블카드 병행 사용",
    },
    "오사카 (일본)": {
        "country": "일본",
        "currency": "JPY",
        "rate": 9.2,
        "lat": 34.6937,
        "lon": 135.5022,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "주유패스 활용 시 교통비 대폭 절감 가능",
    },
    "오키나와 (일본)": {
        "country": "일본",
        "currency": "JPY",
        "rate": 9.2,
        "lat": 26.2124,
        "lon": 127.6809,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "대중교통보다는 렌터카 여행이 필수적인 지역",
    },
    "타이페이 (대만)": {
        "country": "대만",
        "currency": "TWD",
        "rate": 42.0,
        "lat": 25.0330,
        "lon": 121.5654,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "이지카드(EasyCard) 하나로 지하철 및 편의점 완벽 연동",
    },
    "상하이 (중국)": {
        "country": "중국",
        "currency": "CNY",
        "rate": 190.0,
        "lat": 31.2304,
        "lon": 121.4737,
        "emergency": "경찰: 110 / 구급: 120",
        "tips": "알리페이(Alipay) 및 위챗페이 카드 연동 필수",
    },
    "파리 (프랑스)": {
        "country": "프랑스",
        "currency": "EUR",
        "rate": 1450.0,
        "lat": 48.8566,
        "lon": 2.3522,
        "emergency": "긴급 콜센터: 112",
        "tips": "소매치기 주의, 지하철 소지품 밀착 관리 필수",
    },
}

# 도시별 검증된 미슐랭 및 로컬 맛집 데이터베이스 (종류, 평점, 미슐랭 여부)
CURATED_RESTAURANTS = {
    "도쿄 (일본)": [
        {
            "name": "스시 사토 (Sushi Sato)",
            "category": "스시 / 오마카세",
            "rating": "⭐ 4.9 (미슐랭 1스타)",
            "desc": "신선한 제철 생선과 완벽한 샤리의 조화",
        },
        {
            "name": "이치란 신주쿠",
            "category": "돈코츠 라멘",
            "rating": "⭐ 4.6",
            "desc": "깊고 진한 육수의 전통 일본 라멘 전문점",
        },
    ],
    "오사카 (일본)": [
        {
            "name": "미쉐린 3스타 하지메 (Hajime)",
            "category": "창작 파인 다이닝",
            "rating": "⭐ 4.9 (미슐랭 3스타)",
            "desc": "예술 작품 같은 플레이팅과 철학이 담긴 코스",
        },
        {
            "name": "타코야키 도톤보리 쿠쿠루",
            "category": "길거리 음식 / 타코야키",
            "rating": "⭐ 4.5",
            "desc": "문어가 통째로 들어간 겉바속촉 오사카 명물",
        },
    ],
    "오키나와 (일본)": [
        {
            "name": "류큐 요기 (Ryukyu Yohgi)",
            "category": "오키나와 전통 향토요리",
            "rating": "⭐ 4.7",
            "desc": "아구 돼지고기 샤브샤브와 전통 해산물 요리",
        },
        {
            "name": "하나사키 아고라",
            "category": "해산물 / 스시",
            "rating": "⭐ 4.6",
            "desc": "에메랄드빛 바다를 보며 즐기는 신선한 회덮밥",
        },
    ],
    "타이페이 (대만)": [
        {
            "name": "딘타이펑 본점 (Din Tai Fung)",
            "category": "딤섬 / 샤오롱바오",
            "rating": "⭐ 4.8 (미슐랭 빕구르망)",
            "desc": "육즙이 가득한 전설적인 대만 만두 맛집",
        },
        {
            "name": "키키 레스토랑 (Kiki Restaurant)",
            "category": "사천 요리",
            "rating": "⭐ 4.7",
            "desc": "매콤한 부추꽃볶음과 연두부 튀김이 일품",
        },
    ],
    "상하이 (중국)": [
        {
            "name": "울트라바이올렛 바이 폴 파레 (Ultraviolet)",
            "category": "하이엔드 아방가르드",
            "rating": "⭐ 4.9 (미슐랭 3스타)",
            "desc": "시청각 효과가 결합된 초특급 미식 경험",
        },
        {
            "name": "남상만두점 (Nangxiang Mantou)",
            "category": "상하이 전통 만두",
            "rating": "⭐ 4.5",
            "desc": "예원 속에서 즐기는 육즙 폭발 대형 게살 만두",
        },
    ],
    "파리 (프랑스)": [
        {
            "name": "르 아르주일 (L'Arpège)",
            "category": "프렌치 파인 다이닝",
            "rating": "⭐ 4.8 (미슐랭 3스타)",
            "desc": "유기농 채소를 중심으로 한 미식의 정수",
        },
        {
            "name": "불랑제리 몽쥬",
            "category": "베이커리 / 디저트",
            "rating": "⭐ 4.7",
            "desc": "겉은 바삭하고 속은 부드러운 정통 바게트와 크루아상",
        },
    ],
}

# 하이엔드 대시보드 스타일링 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .hero-banner { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 30px; border-radius: 16px; color: white; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); }
    .card { background-color: #ffffff; padding: 22px; border-radius: 14px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .section-title { font-size: 17px; font-weight: 700; color: #0f172a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    .route-card { background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e2e8f0; }
    .rest-card { background-color: #fffbeb; border: 1px solid #fde68a; padding: 12px 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 상단 히어로 배너
st.markdown("""
    <div class="hero-banner">
        <span style="background-color: #3b82f6; color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">PREMIUM AI VOYAGE DESK</span>
        <h1 style="margin: 10px 0 6px 0; font-size: 26px; font-weight: 800;">🌍 미슐랭 맛집 & 실시간 동선 인텔리전스</h1>
        <p style="margin: 0; color: #94a3b8; font-size: 13px;">아시아 주요 명소부터 유럽까지, 검증된 미슐랭 맛집과 최적화 예산안을 한눈에 확인하세요.</p>
    </div>
""", unsafe_allow_html=True)

# 사이드바 입력 허브
st.sidebar.markdown("### ✈️ 여행 조건 설정")
selected_destination = st.sidebar.selectbox(
    "여행지 선택", list(GLOBAL_DESTINATIONS.keys())
)
duration = st.sidebar.selectbox(
    "여행 일정", ["2박 3일", "3박 4일", "4박 5일", "5박 6일"], index=1
)
total_budget_krw = st.sidebar.number_input(
    "총 예산 한도 (원화 기준)", min_value=300000, value=1500000, step=100000
)

dest_info = GLOBAL_DESTINATIONS[selected_destination]
restaurants = CURATED_RESTAURANTS.get(selected_destination, [])

# 메인 레이아웃 분할
col_left, col_right = st.columns([1.6, 1.2])

with col_left:
  # 1. 일자별 스마트 동선 최적화 플랜
  days_num = int(duration[0])
  st.markdown(
      f'<div class="card"><div class="section-title">🗺️ [{selected_destination}]'
      f" {duration} 동선 최적화 마스터 플랜</div>",
      unsafe_allow_html=True,
  )

  for d in range(1, days_num + 1):
    m_query = f"{selected_destination.split(' ')[0]} 관광 랜드마크"
    l_query = f"{selected_destination.split(' ')[0]} 맛집"
    n_query = f"{selected_destination.split(' ')[0]} 야경"

    url_m = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(m_query)}"
    url_l = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(l_query)}"
    url_n = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(n_query)}"

    st.markdown(
        f"""
            <div class="route-card">
                <b>📅 Day {d} 추천 루트 코스</b><br>
                <div style="margin-top: 6px; font-size: 13px; color: #334155;">
                    • <b>오전 스팟</b>: 핵심 랜드마크 탐방 [<a href="{url_m}" target="_blank" style="color: #2563eb; text-decoration: none;">📍 구글맵</a>]<br>
                    • <b>오후 미식</b>: 현지 로컬 맛집 투어 [<a href="{url_l}" target="_blank" style="color: #2563eb; text-decoration: none;">📍 맛집위치</a>]<br>
                    • <b>저녁 일정</b>: 야경 명소 및 디너 코스 [<a href="{url_n}" target="_blank" style="color: #2563eb; text-decoration: none;">📍 야경스팟</a>]
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 미슐랭 및 카테고리별 검증된 맛집 큐레이션 섹션
  st.markdown(
      f'<div class="card"><div class="section-title">🍽️ [{selected_destination}]'
      " 미슐랭 & 로컬 베스트 맛집 큐레이션</div>",
      unsafe_allow_html=True,
  )

  for rest in restaurants:
    rest_map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(rest['name'])}"
    st.markdown(
        f"""
            <div class="rest-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b>🍴 {rest['name']}</b>
                    <span style="font-size: 12px; font-weight: 700; color: #d97706;">{rest['rating']}</span>
                </div>
                <div style="font-size: 12px; color: #475569; margin-top: 4px;"><b>종류</b>: {rest['category']}</div>
                <div style="font-size: 13px; color: #1e293b; margin-top: 4px;">{rest['desc']}</div>
                <div style="margin-top: 6px; text-align: right;">
                    <a href="{rest_map_url}" target="_blank" style="font-size: 12px; color: #2563eb; text-decoration: none; font-weight: 600;">👉 구글맵에서 위치 및 후기 확인</a>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

with col_right:
  # 3. 실시간 예산 역산
  st.markdown(
      '<div class="card"><div class="section-title">💰 실시간 예산 환산 리포트</div>',
      unsafe_allow_html=True,
  )
  curr_code = dest_info["currency"]
  rate = dest_info["rate"]

  if curr_code == "JPY":
    local_budget = (total_budget_krw / rate) * 100
    budget_str = f"약 {local_budget:,.0f} 엔 (JPY)"
  elif curr_code == "TWD":
    local_budget = total_budget_krw / rate
    budget_str = f"약 {local_budget:,.0f} 타이완 달러 (TWD)"
  elif curr_code == "CNY":
    local_budget = total_budget_krw / rate
    budget_str = f"약 {local_budget:,.0f} 위안 (CNY)"
  else:
    local_budget = total_budget_krw / rate
    budget_str = f"약 {local_budget:,.2f} {curr_code}"

  st.metric(label="설정 총 예산 (원화)", value=f"{total_budget_krw:,} 원")
  st.metric(label=f"현지 통화 환산 가치 ({curr_code})", value=budget_str)

  budget_breakdown = {
      "지출 항목": ["숙박비 (Hotel)", "식비 및 미슐랭", "교통비 및 이동", "쇼핑 및 비상금"],
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

  # 4. 지도 레이더 및 비상 연락망
  st.markdown(
      '<div class="card"><div class="section-title">🛰️ 거점 위치 레이더 & 팁</div>',
      unsafe_allow_html=True,
  )
  map_df = pd.DataFrame([{
      "lat": dest_info["lat"],
      "lon": dest_info["lon"],
      "name": selected_destination,
  }])
  st.map(map_df, latitude="lat", longitude="lon", size=300, zoom=10)

  st.markdown(
      f"""
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 10px; border-radius: 8px; margin-top: 12px; font-size: 12px; color: #991b1b;">
            <b>📞 현지 긴급 연락처</b><br>{dest_info['emergency']}
        </div>
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px; border-radius: 8px; margin-top: 8px; font-size: 12px; color: #166534;">
            <b>💡 스마트 팁</b><br>{dest_info['tips']}
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)
