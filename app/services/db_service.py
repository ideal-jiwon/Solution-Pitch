import psycopg2
import os

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def insert_review_analysis(review_id, category, sentiment_score, key_phrases, summary):
    """
    리뷰 분석 데이터를 PostgreSQL에 저장
    """
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO review_analysis (review_id, category, sentiment_score, key_phrases, summary)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (review_id) DO NOTHING;
    """
    cursor.execute(insert_query, (review_id, category, sentiment_score, key_phrases, summary))

    conn.commit()
    cursor.close()
    conn.close()