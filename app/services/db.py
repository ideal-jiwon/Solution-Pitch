import psycopg2
import os

def connect_db():
    """PostgreSQL 데이터베이스 연결"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT", 5432)
    )

def create_tables():
    """PostgreSQL 테이블 생성"""
    conn = connect_db()
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_reviews (
        place_id TEXT,
        review_id TEXT PRIMARY KEY,
        review_text TEXT,
        rating TEXT
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()

    print("✅ PostgreSQL: `raw_reviews` 테이블이 생성되었습니다!")

