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

@models_bp.route("/compare_reviews", methods=["GET"])
def compare_reviews():
    business_id = request.args.get("business_id")
    if not business_id:
        return jsonify({"error": "Missing business_id"}), 400

    conn = connect_db()
    cursor = conn.cursor()


    cursor.execute("SELECT city FROM businesses WHERE business_id = %s", (business_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"error": "Business not found"}), 404
    city = row[0]

    cursor.execute("SELECT text FROM reviews WHERE business_id = %s LIMIT 30", (business_id,))
    my_reviews = [r[0] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT r.text FROM reviews r
        JOIN businesses b ON r.business_id = b.business_id
        WHERE b.city = %s AND r.business_id != %s
        LIMIT 100
    """, (city, business_id))
    other_reviews = [r[0] for r in cursor.fetchall()]

    cursor.close()
    conn.close()

    def analyze_group(reviews):
        category_scores = {}
        category_count = {}

        for text in reviews:
            sentiment, confidence = analyze_sentiment(text)
            category = classify_category(text)

            if category not in category_scores:
                category_scores[category] = 0
                category_count[category] = 0

            category_scores[category] += confidence.get("positive", 0)
            category_count[category] += 1

        return {
            category: category_scores[category] / category_count[category]
            for category in category_scores
        }

    my_scores = analyze_group(my_reviews) if my_reviews else {}
    others_scores = analyze_group(other_reviews) if other_reviews else {}

    return jsonify({
        "business_id": business_id,
        "city": city,
        "my_scores": my_scores,
        "nearby_scores": others_scores
    }), 200
