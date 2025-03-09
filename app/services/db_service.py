import psycopg2
import os

DB_CONFIG = {
    "dbname": "yourdb",
    "user": "youruser",
    "password": "yourpassword",
    "host": "localhost",
    "port": "5432",
}

def connect_db():
    """PostgreSQL DB 연결"""
    return psycopg2.connect(**DB_CONFIG)

def insert_review_analysis(review_id, category, sentiment_score, keywords, summary):
    """NLP 분석 결과를 review_analysis 테이블에 저장"""
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO review_analysis (review_id, category, sentiment_score, keywords, summary)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (review_id) DO NOTHING
    """, (review_id, category, sentiment_score["positive"], keywords, summary))

    conn.commit()
    cur.close()
    conn.close()

def fetch_unprocessed_reviews():
    """NLP 처리가 안 된 리뷰 가져오기"""
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT review_id, cleaned_text FROM cleaned_reviews 
        WHERE review_id NOT IN (SELECT review_id FROM review_analysis)
    """)
    reviews = cur.fetchall()

    cur.close()
    conn.close()
    return reviews
