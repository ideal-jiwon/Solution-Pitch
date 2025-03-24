# app/dashboard/main.py

import os
import streamlit as st
import pandas as pd
import psycopg2

# 🔹 Streamlit 페이지 설정
st.set_page_config(page_title="📊 Koala SolutionPitch DB", layout="wide")

# 🔹 PostgreSQL에서 분석된 리뷰 불러오기
@st.cache_data
def load_data():
    conn = psycopg2.connect(
        host="localhost",
        dbname="restaurant_ai",
        user="stellam",
        password="stella1004"
    )
    query = """
        SELECT 
            b.name AS business_name,
            b.address,
            a.review_id,
            r.review_text,
            a.sentiment_score,
            a.key_phrases,
            a.summary
        FROM review_analysis a
        JOIN reviews r ON a.review_id = r.review_id
        JOIN businesses b ON r.business_id = b.business_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 🔹 데이터 로딩
df = load_data()

# 🔹 대시보드 UI 구성
st.title("📍 상업 리뷰 분석 대시보드")
st.markdown("리뷰 데이터를 바탕으로 감성 분석, 핵심 키워드 추출, 요약 결과를 확인할 수 있습니다.")

# 🔸 선택 박스: 비즈니스 선택
business_list = df["business_name"].unique()
selected_business = st.selectbox("상점을 선택하세요", business_list)

# 🔸 필터링
filtered_df = df[df["business_name"] == selected_business]

# 🔹 상점 정보 출력
if not filtered_df.empty:
    st.subheader(f"🏢 {selected_business}")
    st.markdown(f"📫 주소: `{filtered_df['address'].iloc[0]}`")
    st.markdown(f"📝 리뷰 수: `{len(filtered_df)}`")

    # 🔹 감성 분포 시각화
    st.subheader("📈 감성 분석 분포")
    sentiment_counts = filtered_df["sentiment_score"].value_counts()
    st.bar_chart(sentiment_counts)

    # 🔹 리뷰 테이블
    st.subheader("🗣 리뷰 요약 및 키워드")
    for idx, row in filtered_df.iterrows():
        st.markdown(f"**리뷰:** {row['review_text']}")
        st.markdown(f"🔹 요약: {row['summary']}")
        st.markdown(f"🔸 감성: `{row['sentiment_score']}`")
        st.markdown(f"🏷️ 키워드: `{', '.join(row['key_phrases'])}`")
        st.markdown("---")
else:
    st.warning("선택한 상점의 리뷰가 없습니다.")
