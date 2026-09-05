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

# 글로벌 도시 확장 DB (환율 및 기본 이미지, 좌표 포함)
GLOBAL_DESTINATIONS = {
    "도쿄 (일본)": {
        "currency": "JPY",
        "rate": 9.2,  # 100엔당 원화 (1엔 = 약 9.2원) -> 200만 원이면 약 217,391엔
        "lat": 35.6762,
        "lon": 139.6503,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "스이카(Suica) 카드 사전 충전 필수",
        "banner_img": (
            "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80"
        ),
    },
    "오사카 (일본)": {
        "currency": "JPY",
        "rate": 9.2,
        "lat": 34.6937,
        "lon": 135.5022,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "주유패스 활용 시 교통비 절감",
        "banner_img": (
            "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=1200&q=80"
        ),
    },
    "오키나와 (일본)": {
        "currency": "JPY",
        "rate": 9.2,
        "lat": 26.2124,
        "lon": 127.6809,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "렌터카 여행 필수",
        "banner_img": (
            "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?auto=format&fit=crop&w=1200&q=80"
        ),
    },
    "타이페이 (대만)": {
        "currency": "TWD",
        "rate": 42.0,  # 1대만달러 = 약 42원
        "lat": 25.0330,
        "lon": 121.5654,
        "emergency": "경찰: 110 / 구급: 119",
        "tips": "이지카드 하나로 완벽 연동",
        "banner_img": (
            "https://images.unsplash.com/photo-1508873696983-2df5c920ac1c?auto=format&fit=crop&w=1200&q=80"
        ),
    },
    "상하이 (중국)": {
        "currency": "CNY",
        "rate": 190.0,  # 1위안 = 약 190원
        "lat": 31.2304,
        "lon": 121.4737,
        "emergency": "경찰: 110 / 구급: 120",
        "tips": "알리페이 및 위챗페이 카드 연동 필수",
        "banner_img": (
            "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80"
        ),
    },
    "파리 (프랑스)": {
        "currency": "EUR",
        "rate": 1450.0,  # 1유로 = 약 1450원
        "lat": 48.8566,
        "lon": 2.3522,
        "emergency": "긴급 콜센터: 112",
        "tips": "소매치기 주의",
        "banner_img": (
            "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80"
        ),
    },
}

# 도시별 구체적인 명소 및 사진, 맛집 큐레이션 데이터베이스
CURATED_TRAVEL_DATA = {
    "상하이 (중국)": {
        "spots": [
            {
                "day": 1,
                "title": "와이탄 (The Bund) & 동방명주 야경",
                "desc": (
                    "상하이의 상징인 유럽풍 건축물 거리와 화려한 미래형 마천루의"
                    " 조화"
                ),
                "img": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=600&q=80",
            },
            {
                "day": 2,
                "title": "예원 (Yuyuan Garden) & 상하이 노거리",
                "desc": (
                    "명나라 시대의 전통 정원과 전통 가옥에서 즐기는 다채로운 길거리"
                    " 간식"
                ),
                "img": "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80",
            },
            {
                "day": 3,
                "title": "난징동루 쇼핑가 & 신천지",
                "desc": "상하이 최대의 번화가 쇼핑 지구와 트렌디한 카페 거리",
                "img": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=600&q=80",
            },
        ],
        "restaurants": [
            {
                "name": "남상만두점 (Nanxiang Mantou)",
                "category": "상하이 전통 만두",
                "rating": "⭐ 4.6 (미슐랭 추천)",
                "desc": "예원에서 맛보는 육즙 가득한 정통 게살 만두",
                "img": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "울트라바이올렛 (Ultraviolet)",
                "category": "하이엔드 아방가르드",
                "rating": "⭐ 4.9 (미슐랭 3스타)",
                "desc": "오감과 시청각 효과가 결합된 초특급 미식 쇼",
                "img": "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
    "도쿄 (일본)": {
        "spots": [
            {
                "day": 1,
                "title": "센소지 & 도쿄 스카이트리",
                "desc": "도쿄에서 가장 오래된 사찰 아사쿠사 센소지와 거대한 타워 전망대",
                "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80",
            },
            {
                "day": 2,
                "title": "시부야 스크램블 교차로 & 미야시타 파크",
                "desc": "세계에서 가장 복잡하지만 질서 정연한 시부야의 심장부",
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
            },
            {
                "day": 3,
                "title": "신주쿠 교엔 & 오모테산도 쇼핑",
                "desc": "도심 속 드넓은 자연 정원과 세련된 건축 디자인 거리",
                "img": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=600&q=80",
            },
        ],
        "restaurants": [
            {
                "name": "스시 사토 (Sushi Sato)",
                "category": "스시 오마카세",
                "rating": "⭐ 4.9 (미슐랭 1스타)",
                "desc": "엄선된 제철 식재료로 빚어내는 장인의 초밥",
                "img": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=600&q=80",
            },
            {
                "name": "이치란 신주쿠 본점",
                "category": "돈코츠 라멘",
                "rating": "⭐ 4.6",
                "desc": "진한 육수와 특제 비밀 소스가 일품인 일본 대표 라멘",
                "img": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80",
            },
        ],
    },
}

# 기본값 처리 (데이터가 없는 도시 선택 시 공통 템플릿 제공)
default_spots = [
    {
        "day": 1,
        "title": "시내 중심가 랜드마크 투어",
        "desc": "도시의 역사와 현대가 공존하는 대표 랜드마크 탐방",
        "img": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80",
    },
    {
        "day": 2,
        "title": "로컬 문화 체험 및 미식 거리",
        "desc": "현지인들이 사랑하는 골목길과 시그니처 로컬 푸드 투어",
        "img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80",
    },
    {
        "day": 3,
        "title": "핵심 쇼핑 및 야경 명소 산책",
        "desc": "여행의 마지막을 화려하게 장식할 쇼핑 지구와 야경 감상",
        "img": "https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?auto=format&fit=crop&w=600&q=80",
    },
]

default_restaurants = [
    {
        "name": "현지 최고 평점 로컬 레스토랑",
        "category": "파인 다이닝 / 로컬 푸드",
        "rating": "⭐ 4.8 (현지인 추천)",
        "desc": "여행객과 현지인 모두에게 사랑받는 시그니처 맛집",
        "img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "미슐랭 빕구르망 선정 식당",
        "category": "모던 퀴진",
        "rating": "⭐ 4.7 (미슐랭 선정)",
        "desc": "합리적인 가격으로 즐기는 최고 수준의 요리",
        "img": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
    },
]

# 감성적인 에어비앤비/토스 하이브리드 스타일 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .hero-banner { padding: 40px; border-radius: 20px; color: white; margin-bottom: 25px; box-shadow: 0 15px 30px -10px rgba(0,0,0,0.3); background-size: cover; background-position: center; position: relative; }
    .hero-overlay { background: linear-gradient(180deg, rgba(15,23,42,0.3) 0%, rgba(15,23,42,0.85) 100%); position: absolute; top: 0; left: 0; right: 0; bottom: 0; border-radius: 20px; z-index: 1; }
    .hero-content { position: relative; z-index: 2; }
    .card { background-color: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-bottom: 20px; }
    .section-title { font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
    .spot-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
    .rest-card { background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; overflow: hidden; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True,)

# 사이드바 입력 허브
st.sidebar.markdown("### ✈️ 스마트 여행 설정")
selected_destination = st.sidebar.selectbox(
    "여행지 선택", list(GLOBAL_DESTINATIONS.keys())
)
duration = st.sidebar.selectbox(
    "여행 일정", ["2박 3일", "3박 4일", "4박 5일", "5박 6일"], index=1
)
total_budget_krw = st.sidebar.number_input(
    "총 예산 한도 (원화 기준)", min_value=300000, value=2000000, step=100000
)

dest_info = GLOBAL_DESTINATIONS[selected_destination]
content_data = CURATED_TRAVEL_DATA.get(
    selected_destination,
    {"spots": default_spots, "restaurants": default_restaurants},
)

# 상단 비주얼 히어로 배너 (선택한 도시의 고화질 배경 사진 적용)
banner_url = dest_info["banner_img"]
st.markdown(
    f"""
    <div class="hero-banner" style="background-image: url('{banner_url}');">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <span style="background-color: #3b82f6; color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;">AI VOYAGE MASTER PLAN</span>
            <h1 style="margin: 12px 0 6px 0; font-size: 30px; font-weight: 900;">✨ {selected_destination} 맞춤형 힐링 여행</h1>
            <p style="margin: 0; color: #cbd5e1; font-size: 14px;">설정하신 예산과 일정에 맞춰 엄선된 명소, 미슐랭 맛집, 실시간 환산 예산이 완벽하게 설계되었습니다.</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# 메인 레이아웃 분할
col_left, col_right = st.columns([1.6, 1.2])

with col_left:
  # 1. 시각적인 사진 카드가 포함된 일자별 명소 큐레이션
  st.markdown(
      f'<div class="card"><div class="section-title">🗺️ [{selected_destination}]'
      f" {duration} 핵심 명소 & 포토스팟 큐레이션</div>",
      unsafe_allow_html=True,
  )

  for spot in content_data["spots"]:
    map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(spot['title'])}"
    st.markdown(
        f"""
        <div class="spot-card">
            <img src="{spot['img']}" style="width: 100%; height: 180px; object-fit: cover;">
            <div style="padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="background-color: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">Day {spot['day']} 스팟</span>
                    <a href="{map_url}" target="_blank" style="font-size: 12px; color: #2563eb; text-decoration: none; font-weight: 600;">📍 구글맵 길찾기</a>
                </div>
                <h4 style="margin: 0 0 6px 0; font-size: 16px; color: #0f172a; font-weight: 700;">{spot['title']}</h4>
                <p style="margin: 0; font-size: 13px; color: #64748b;">{spot['desc']}</p>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

  # 2. 미슐랭 및 로컬 맛집 시각화 카드
  st.markdown(
      f'<div class="card"><div class="section-title">🍽️ [{selected_destination}]'
      " 미슐랭 & 시그니처 맛집 리스트</div>",
      unsafe_allow_html=True,
  )

  for rest in content_data["restaurants"]:
    rest_map_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(rest['name'])}"
    st.markdown(
        f"""
        <div class="rest-card">
            <img src="{rest['img']}" style="width: 100%; height: 160px; object-fit: cover;">
            <div style="padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <h4 style="margin: 0; font-size: 15px; color: #0f172a; font-weight: 700;">{rest['name']}</h4>
                    <span style="font-size: 12px; font-weight: 700; color: #d97706;">{rest['rating']}</span>
                </div>
                <div style="font-size: 12px; color: #b45309; font-weight: 600; margin-bottom: 6px;">{rest['category']}</div>
                <p style="margin: 0 0 10px 0; font-size: 13px; color: #475569;">{rest['desc']}</p>
                <div style="text-align: right;">
                    <a href="{rest_map_url}" target="_blank" style="font-size: 12px; color: #2563eb; text-decoration: none; font-weight: 600;">👉 구글맵에서 위치 및 후기 확인</a>
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
  st.markdown("</div>", unsafe_allow_html=True)

with col_right:
  # 3. 올바르게 수정된 실시간 예산 환산 리포트
  st.markdown(
      '<div class="card"><div class="section-title">💰 실시간 예산 환산 리포트</div>',
      unsafe_allow_html=True,
  )

  curr_code = dest_info["currency"]
  rate = dest_info["rate"]

  # 정확한 환산 로직 계산
  if curr_code == "JPY":
    local_budget = (total_budget_krw / rate) * 100
    budget_str = f"약 {local_budget:,.0f} 엔 (JPY)"
  else:
    local_budget = total_budget_krw / rate
    budget_str = f"약 {local_budget:,.0f} {curr_code}"

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

  # 4. 지도 레이더 & 비상 연락망
  st.markdown(
      '<div class="card"><div class="section-title">🛰️ 목적지 거점 레이더 & 팁</div>',
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
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 12px; border-radius: 8px; margin-top: 15px; font-size: 13px; color: #991b1b;">
            <b>📞 현지 긴급 연락처</b><br>{dest_info['emergency']}
        </div>
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 8px; margin-top: 10px; font-size: 13px; color: #166534;">
            <b>💡 스마트 여행 팁</b><br>{dest_info['tips']}
        </div>
    """,
      unsafe_allow_html=True,
  )
  st.markdown("</div>", unsafe_allow_html=True)
