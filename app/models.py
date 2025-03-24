from flask import Blueprint, request, jsonify
from app.services.db import connect_db
from app.services.nlp_service import analyze_sentiment, extract_key_phrases, classify_category

models_bp = Blueprint("models", __name__)

@models_bp.route("/realtime_sentiment", methods=["GET"])
def realtime_sentiment():
    business_id = request.args.get("business_id")
    if not business_id:
        return jsonify({"error": "Missing business_id parameter"}), 400

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT review_id, text FROM reviews WHERE business_id = %s LIMIT 10", (business_id,))
    reviews = cursor.fetchall()

    if not reviews:
        return jsonify({"error": "No reviews found"}), 404

    analyzed_reviews = []

    for review_id, review_text in reviews:
        sentiment, confidence_scores = analyze_sentiment(review_text)
        key_phrases = extract_key_phrases(review_text)
        category = classify_category(review_text)

        analyzed_reviews.append({
            "review_id": review_id,
            "sentiment": sentiment,
            "confidence": confidence_scores,
            "keywords": key_phrases,
            "category": category
        })

    cursor.close()
    conn.close()

    return jsonify({
        "business_id": business_id,
        "analyzed_reviews": analyzed_reviews
    })

