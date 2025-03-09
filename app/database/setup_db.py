import psycopg2
import os
from dotenv import load_dotenv

# 🔹 .env 파일을 강제 로드
ENV_PATH = "/Users/stellam/restaurant-ai-backend/restaurant-ai-frontend-typescript/.env"

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    print(f"✅ .env file loaded from {ENV_PATH}")
else:
    print(f"⚠ Warning: .env file not found at {ENV_PATH}")

# 🔹 환경 변수에서 DB 정보 가져오기
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432"),
}

def setup_database():
    """PostgreSQL에 테이블을 생성하는 함수"""
    try:
        print(f"🔹 Connecting to database: {DB_CONFIG['dbname']} at {DB_CONFIG['host']} as {DB_CONFIG['user']}")

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 🔹 schema.sql 파일 로드
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        
        if not os.path.exists(schema_path):
            print("❌ Error: schema.sql 파일을 찾을 수 없습니다.")
            return

        with open(schema_path, "r") as f:
            sql_commands = f.read()

        cur.execute(sql_commands)  # SQL 실행
        conn.commit()
        
        print("✅ Database setup complete! Table 'review_analysis' is created.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    setup_database()
