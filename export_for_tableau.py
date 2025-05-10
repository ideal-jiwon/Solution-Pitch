import os
import pandas as pd
from dotenv import load_dotenv
from app.services.db import connect_db

load_dotenv()

EXPORT_PATH="exports/tableau_report.csv"

def export_tableau_csv():
    conn = connect_db()
    query= """
        SELECT
            r.review_id,
            r.business_id,
            b.name AS business_name,
            b.city,
            b.state,
            b.categories,
            r.date,
            r.stars,
            r.sentiment_label,
            r.sentiment_score,
            r.key_phrases
        FROM reviews r
        JOIN businesses b ON r.business_id = b.business_id
        WHERE r.sentiment_label IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    os.makedirs("exports", exist_ok=True)
    df.to_csv(EXPORT_PATH, index=False)
    print(f"Exported data to {EXPORT_PATH}")

if __name__ == "__main__":
    export_tableau_csv()