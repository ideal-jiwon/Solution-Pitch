from flask import request, jsonify, send_from_directory, session
import requests
import openai
import os
from app.nlp_models import analyze_sentiment

def setup_routes(app):
    """Flask 라우트를 설정하는 함수"""

    # 🔹 정적 파일 제공 (HTML, CSS, JS)
    @app.route("/")
    def serve_index():
        return send_from_directory("public", "index.html")

    @app.route("/<path:path>")
    def serve_static_files(path):
        return send_from_directory("public", path)

    # 🔹 Google 로그인 URL 생성
    @app.route("/auth/login")
    def login():
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            "?response_type=code"
            f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
            "&redirect_uri=" + os.getenv("GOOGLE_REDIRECT_URI") +
            "&scope=openid%20email%20profile"
        )
        return jsonify({"auth_url": google_auth_url})

    # 🔹 감정 분석 API
    @app.route("/analyze_sentiment", methods=["POST"])
    def sentiment_analysis():
        data = request.json
        if "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        sentiment, confidence = analyze_sentiment(data["text"])
        return jsonify({"sentiment": sentiment, "confidence": confidence})
