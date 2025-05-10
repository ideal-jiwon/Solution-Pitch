import json
import os
import pandas as pd
import csv

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from app.services.db import connect_db
from app.services.nlp_service import analyze_sentiment, extract_key_phrases

load_dotenv()

AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY")
AZURE_STORAGE_URL = "https://restaurantimagestorage.blob.core.windows.net"
CONTAINER_NAME = "restaurantreviews"

def download_blob(blob_name, local_path):
    service = BlobServiceClient(account_url=AZURE_STORAGE_URL, credential=AZURE_STORAGE_KEY)
    blob = service.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    with open(local_path, "wb") as f:
        f.write(blob.download_blob().readall())
    print(f"Downloaded {blob_name} to {local_path}")

def copy_csv_to_postgres(csv_path, table_name, columns):
    conn = connect_db()
    cursor = conn.cursor()
    with open(csv_path, "r", encoding="utf-8") as f:
        next(f)  # skip header
        cursor.copy_expert(f"""
            COPY {table_name} ({columns})
            FROM STDIN WITH CSV NULL '\\N'
        """, f)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Data copied to {table_name} from {csv_path}")

def truncate_table(table_name):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Truncated table {table_name}")


def clean_business_csv(path):
     df = pd.read_csv(path)

     df = df[df["business_id"].notnull()]
     df = df[~df["business_id"].astype(str).str.contains("#NAME?", na=False)]

     df.drop_duplicates(subset=["business_id"], inplace=True)

     df.to_csv(path, index=False)
     print("cleaned business.csv")

def clean_review_csv(path):

    df = pd.read_csv(path, dtype=str, low_memory=False)
    
    # remove nulls in key fields
    df = df.dropna(subset=["review_id", "business_id", "user_id", "stars", "date", "text", "useful", "funny", "cool"])
 
    df = df[~df["review_id"].astype(str).str.contains("#NAME?", na=False)]
    df = df[~df["business_id"].astype(str).str.contains("#NAME?", na=False)]
    df = df[pd.to_numeric(df['stars'], errors='coerce').notnull()]
    df['stars'] = df['stars'].astype(float)

    business_df = pd.read_csv("temp/business.csv", dtype=str)
    valid_business_ids = set(business_df["business_id"])
    df = df[df["business_id"].isin(valid_business_ids)]

    for col in ["useful", "funny", "cool"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df[df[col].notnull()]
        df[col] = df[col].astype(int)

    df.drop_duplicates(subset=["review_id"], inplace=True)
    df.to_csv(path, index=False, quoting=csv.QUOTE_ALL)
    print("Cleaned review.csv")


def insert_all():
    os.makedirs("temp", exist_ok=True)

    download_blob("business.csv", "temp/business.csv")
    download_blob("review.csv", "temp/review.csv")
    
    #data cleaning
    clean_business_csv("temp/business.csv")
    clean_review_csv("temp/review.csv")

    #avoiding duplicates
    truncate_table("reviews")
    truncate_table("businesses")

    copy_csv_to_postgres(
        "temp/business.csv",
        "businesses",
        "business_id, name, address, city, state, postal_code, latitude, longitude, categories, hours, review_count, stars, is_open"
    )

    try:
        copy_csv_to_postgres(
        "temp/review.csv",
        "reviews",
        "review_id, business_id, user_id, stars, date, text, useful, funny, cool"
    )
    except Exception as e:
        print("❌ COPY failed:", e)

def analyze_and_update_reviews():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT review_id, text FROM reviews WHERE sentiment_label IS NULL LIMIT 1000")
    reviews = cursor.fetchall()

    for review_id, review_text in reviews:
        sentiment, scores = analyze_sentiment(review_text)
        key_phrases = extract_key_phrases(review_text)
        score = scores.get("positive", 0.0)

        cursor.execute("""
                       UPDATE reviews
                       SET sentiment_label = %s, sentiment_score = %s, key_phrases = %s
                       WHERE review_id = %s
        """, (sentiment, score, json.dumps(key_phrases), review_id))

    conn.commit()
    cursor.close()
    conn.close()
    print("analysis done")


if __name__ == "__main__":
    insert_all()
    analyze_and_update_reviews()
