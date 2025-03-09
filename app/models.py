from flask import Blueprint, request, jsonify
import logging
from app.services.nlp_service import analyze_sentiment, extract_key_phrases, summarize_text
from app.services.db_service import insert_review_analysis, fetch_unprocessed_reviews

models_bp = Blueprint("models", __name__)

@models_bp.route("/analyze_reviews", methods=["GET"])
def analyze_reviews():
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "Missing place_id"}), 400

    unprocessed_reviews = fetch_unprocessed_reviews()

    if not unprocessed_reviews:
        return jsonify({"message": "No new reviews to analyze"}), 200

    results = []
    for review_id, text in unprocessed_reviews:
        category, sentiment_score = analyze_sentiment(text)
        key_phrases = extract_key_phrases(text)
        summary = summarize_text(text)

        insert_review_analysis(review_id, category, sentiment_score, key_phrases, summary)

        results.append({
            "review_id": review_id,
            "category": category,
            "sentiment_score": sentiment_score,
            "keywords": key_phrases,
            "summary": summary
        })

    return jsonify({"message": "Reviews analyzed and stored", "results": results})
