import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from app.services.db import connect_db


def insert_businesses(csv_path):
    df = pd.read_csv(csv_path)
    conn = connect_db()
    cursor = conn.cursor()

    df["hours"] = df["hours"].apply(lambda h: None if pd.isna(h) or h == "\\N" else h)
    df["is_open"] = df["is_open"].apply(lambda x: str(x).lower() == "true")

    values = [
        (
            str(row["business_id"]),
            str(row["name"]),
            str(row["address"]),
            str(row["city"]),
            str(row["state"]),
            str(row["postal_code"]),
            float(row["latitude"]),
            float(row["longitude"]),
            str(row["categories"]),
            row["hours"],
            int(row["review_count"]),
            float(row["stars"]),
            bool(row["is_open"])
        )
        for _, row in df.iterrows()
    ]

    query = """
        INSERT INTO businesses (
            business_id, name, address, city, state, postal_code,
            latitude, longitude, categories, hours,
            review_count, stars, is_open
        ) VALUES %s
        ON CONFLICT (business_id) DO NOTHING;
    """
    execute_values(cursor, query, values, page_size=1000)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ businesses 삽입 완료")

def insert_reviews(csv_path):
    conn = connect_db()
    cursor = conn.cursor()

    chunk_size = 10000

    try:
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            chunk.dropna(subset=["review_id"], inplace=True)
            chunk.drop_duplicates(subset=["review_id"], inplace=True)

            # 안전한 타입 변환
            chunk.fillna({
                "text": "",
                "stars": 0,
                "useful": 0,
                "funny": 0,
                "cool": 0
            }, inplace=True)

            chunk["stars"] = pd.to_numeric(chunk["stars"], errors="coerce").fillna(0).astype(int)
            chunk["useful"] = pd.to_numeric(chunk["useful"], errors="coerce").fillna(0).astype(int)
            chunk["funny"] = pd.to_numeric(chunk["funny"], errors="coerce").fillna(0).astype(int)
            chunk["cool"] = pd.to_numeric(chunk["cool"], errors="coerce").fillna(0).astype(int)
            chunk["place_id"] = chunk.get("place_id", "UNKNOWN")

            values = [
                (
                    str(row["review_id"]),
                    str(row["business_id"]),
                    int(row["stars"]),
                    str(row["date"]),
                    str(row["text"]),
                    int(row["useful"]),
                    int(row["funny"]),
                    int(row["cool"]),
                    str(row["place_id"])
                )
                for _, row in chunk.iterrows()
            ]

            query = """
                INSERT INTO reviews (
                    review_id, business_id, stars, date,
                    text, useful, funny, cool, place_id
                ) VALUES %s;
            """

            try:
                # 🔍 디버깅용 출력
                print("쿼리 확인:", query)
                print("예시 values:", values[0])

                execute_values(
                    cursor,
                    query,
                    values,
                    template="(%s, %s, %s, %s, %s, %s, %s, %s, %s)",  # 👈 핵심!!
                    page_size=1000
                )
                conn.commit()
                print(f"✅ 청크 {len(values)}건 삽입 완료")
            except Exception as e:
                print(f"❌ 청크 삽입 중 에러 발생: {e}")
                conn.rollback()

    finally:
        cursor.close()
        conn.close()
        print("✅ 전체 reviews 삽입 작업 종료")




if __name__ == "__main__":
    insert_businesses("/Users/stellam/Desktop/temp/business.csv")
    insert_reviews("/Users/stellam/Desktop/temp/review.csv")
