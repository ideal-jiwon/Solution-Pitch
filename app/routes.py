from flask import Blueprint, request, jsonify
import requests
import os
from app.nlp_models import categorize_review, analyze_review_relationships, sentiment_analyzer

main_bp = Blueprint("main", __name__)

@main_bp.route("/analyze_reviews", methods=["GET"])
def analyze_reviews():
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "Missing place_id"}), 400

    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,reviews&key={os.getenv('GOOGLE_PLACES_API_KEY')}"
    response = requests.get(url)
    data = response.json()

    if "reviews" not in data.get("result", {}):
        return jsonify({"error": "No reviews found"})

    reviews = data["result"]["reviews"]
    processed_reviews = []

    for review in reviews:
        sentiment = sentiment_analyzer(review["text"])[0]
        categories = categorize_review(review["text"])

        processed_reviews.append({
            "author": review["author_name"],
            "rating": review["rating"],
            "text": review["text"],
            "sentiment": sentiment["label"],
            "confidence": sentiment["score"],
            "categories": categories
        })

    analysis_result = analyze_review_relationships(processed_reviews)

    return jsonify({
        "reviews": processed_reviews,
        "relationship_analysis": analysis_result
    })



