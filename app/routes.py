from flask import request, jsonify, send_from_directory
from app.nlp import fetch_reviews, analyze_review_relationships
import os

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../public")

def setup_routes(app):
    """Flask 라우트 설정"""

    @app.route("/")
    def serve_index():
        return send_from_directory(PUBLIC_DIR, "index.html")

    @app.route("/<path:path>")
    def serve_static_files(path):
        return send_from_directory(PUBLIC_DIR, path)

    @app.route("/analyze_reviews", methods=["GET"])
    def analyze_reviews():
        place_id = request.args.get("place_id")
        if not place_id:
            return jsonify({"error": "Missing place_id"}), 400

        result = fetch_reviews(place_id)
        result["relationship_analysis"] = analyze_review_relationships(result["reviews"])
        
        return jsonify(result)

