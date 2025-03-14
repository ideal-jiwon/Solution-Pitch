from flask import Blueprint, request, jsonify
import psycopg2
import os
from app.services.scraper import scrape_reviews
from app.services.db import connect_db

models_bp = Blueprint("models", __name__)

# PostgreSQL 연결 설정
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def connect_db():
    """PostgreSQL 연결"""
    return psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)

def fetch_raw_reviews(place_id):
    """PostgreSQL에서 Raw 리뷰 데이터 가져오기"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT review_id, review_text, rating FROM raw_reviews WHERE place_id = %s", (place_id,))
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()

    return [{"review_id": row[0], "text": row[1], "rating": row[2]} for row in reviews]

@models_bp.route("/analyze_reviews", methods=["GET"])
def analyze_reviews():
    """Raw 리뷰 데이터를 PostgreSQL에서 가져와 반환"""
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "Missing place_id"}), 400
    
    # 🔹 분석 로직 실행
    reviews = scrape_reviews(place_id)
    if not reviews:
        return jsonify({"message": "No reviews found"}), 200

    # 📌 PostgreSQL에 저장
    conn = connect_db()
    cursor = conn.cursor()

    for review in reviews:
        cursor.execute(
            "INSERT INTO raw_reviews (place_id, review_id, review_text, rating) VALUES (%s, %s, %s, %s) ON CONFLICT (review_id) DO NOTHING",
            (place_id, review["review_id"], review["text"], review["rating"])
        )
    
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Reviews successfully scraped and stored",
        "reviews": reviews
    })