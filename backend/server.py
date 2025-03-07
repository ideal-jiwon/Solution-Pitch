import openai
from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import requests
from transformers import pipeline
import json
from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv


# 🔹 환경 변수 로드
load_dotenv()

# 🔹 현재 `server.py`의 경로를 기준으로 `public/` 폴더의 절대 경로 찾기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 프로젝트 루트 경로
PUBLIC_DIR = os.path.join(BASE_DIR, "public")  # public 폴더 경로

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path="")
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app)


# 🔹 Google OAuth 설정
GOOGLE_CLIENT_ID = "888167258223-s9r7egdalka0tvvettboc75qfcm21r5d.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://localhost:5000/auth/callback"

GOOGLE_PLACES_API_KEY = "AIzaSyCcqraspdA5PdAI6mZQTElHBEkDRK0KY5A"
AZURE_OPENAI_API_KEY="AmO7fs6GbfsDFwi2KFcTTZILxclkljZxsEhprX03xHb7TfMlxfMaJQQJ99BCACYeBjFXJ3w3AAABACOG6JA0"
AZURE_OPENAI_ENDPOINT = "https://azure-services-openai.openai.azure.com/"


# 🔹 기본 페이지 제공 (index.html)
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

# 🔹 정적 파일 제공 (CSS, JS, 이미지 등)
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(PUBLIC_DIR, path)

if __name__ == "__main__":
    print(f"🚀 Flask 서버 실행 중: http://127.0.0.1:5000/")
    print(f"📂 Static files served from: {PUBLIC_DIR}")
    app.run(debug=True, port=5000)


# 🔹 Google 로그인 URL 생성
@app.route("/auth/login")
def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        "&redirect_uri=" + GOOGLE_REDIRECT_URI +
        "&scope=openid%20email%20profile"
    )
    return jsonify({"auth_url": google_auth_url})

# 🔹 Google 로그인 콜백 처리
@app.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No authorization code provided"}), 400

    # 🔹 Access Token 요청
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    token_info = token_response.json()

    if "access_token" not in token_info:
        return jsonify({"error": "Failed to obtain access token"}), 400

    access_token = token_info["access_token"]

    # 🔹 Google 사용자 정보 요청
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(userinfo_url, headers=headers)
    user_info = userinfo_response.json()

    # 세션에 사용자 정보 저장
    session["user"] = user_info

    return redirect("http://localhost:5500/home.html")  # 로그인 성공 후 리디렉션

# 🔹 사용자 정보 가져오기
@app.route("/auth/user", methods=["GET"])
def get_user():
    if "user" in session:
        return jsonify(session["user"])
    return jsonify({"error": "User not logged in"}), 401

# 🔹 로그아웃
@app.route("/auth/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)




# 감정 분석 모델 로드 (Hugging Face 모델 사용)
sentiment_analyzer = pipeline("sentiment-analysis")

# 🔹 서비스, 가격, 메뉴, 위치, 분위기 관련 키워드 목록
CATEGORY_KEYWORDS = {
    "price": ["price", "expensive", "cheap", "affordable", "cost", "overpriced"],
    "scale": ["big", "small", "seating", "capacity", "crowded"],
    "convenience": ["location", "parking", "easy", "accessible"],
    "taste": ["delicious", "flavor", "taste", "spicy", "sweet"],
    "menu_variety": ["menu", "options", "variety", "selection"],
    "service": ["staff", "waiter", "service", "friendly", "rude"],
    "exterior": ["outside", "building", "view"],
    "interior": ["inside", "decor", "design"],
    "ambiance": ["atmosphere", "music", "lighting"],
    "cleanliness": ["clean", "hygiene", "dirty"]
}


def categorize_review(text):
    """리뷰를 서비스, 가격, 메뉴, 위치, 분위기 기준으로 분류"""
    categories = {"service": 0, "price": 0, "menu": 0, "location": 0, "ambiance": 0}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text.lower():
                categories[category] += 1  # 해당 카테고리의 점수 증가

    return categories

def fetch_reviews(place_id):
    """Google Places API에서 리뷰를 가져오고 감정 분석 및 카테고리 분류 수행"""
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,reviews&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "reviews" not in data.get("result", {}):
        return {"error": "No reviews found"}

    reviews = data["result"]["reviews"]
    
    category_scores = {"service": [], "price": [], "menu": [], "location": [], "ambiance": []}
    
    processed_reviews = []
    for review in reviews:
        sentiment = sentiment_analyzer(review["text"])[0]  # 감정 분석 수행
        categories = categorize_review(review["text"])  # 리뷰의 카테고리 분석

        # 감정 점수를 별점(1~5점)으로 변환
        score = round(sentiment["score"] * 5)  # 감정 점수를 1~5점으로 변환

        for category, count in categories.items():
            if count > 0:  # 해당 카테고리와 관련된 키워드가 있으면
                category_scores[category].append(score)

        processed_reviews.append({
            "author": review["author_name"],
            "rating": review["rating"],
            "text": review["text"],
            "time": review["relative_time_description"],
            "sentiment": sentiment["label"],  # 감정 분석 결과 (POSITIVE, NEGATIVE, NEUTRAL)
            "confidence": sentiment["score"],  # 감정 분석 확신도
            "categories": categories  # 해당 리뷰가 어느 카테고리에 포함되는지 표시
        })

    # 각 카테고리별 평균 점수 계산
    avg_scores = {category: round(sum(scores) / len(scores), 1) if scores else "-" for category, scores in category_scores.items()}

    return {"reviews": processed_reviews, "avg_scores": avg_scores}

def analyze_review_relationships(reviews):
    """Azure OpenAI를 사용하여 리뷰 간 관계 분석"""
    review_texts = "\n".join([review["text"] for review in reviews])
    
    prompt = f"""
    Analyze the following restaurant reviews and identify key relationships between service, price, menu, location, and ambiance.
    Provide insights on patterns, correlations, and potential improvements:
    {review_texts}
    """

    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        api_key=AZURE_OPENAI_API_KEY,
        base_url=AZURE_OPENAI_ENDPOINT
    )

    return response["choices"][0]["message"]["content"]

@app.route("/analyze_reviews", methods=["GET"])
def analyze_reviews():
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "Missing place_id"}), 400

    result = fetch_reviews(place_id)
    result["relationship_analysis"] = analyze_review_relationships(result["reviews"])
    
    # Add strengths, weaknesses, and ranking analysis
    result["analysis"] = calculate_strengths_weaknesses(result["reviews"])
    result["ranking"] = calculate_restaurant_rank(place_id)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

@app.route("/chat", methods=["POST"])
def chat():
    """Azure OpenAI 기반 챗봇 응답 생성"""
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response = openai.ChatCompletion.create(
        engine="gpt-4",
        messages=[{"role": "system", "content": "Answer based on restaurant review analysis."},
                  {"role": "user", "content": user_input}],
        api_key=AZURE_OPENAI_API_KEY,
        base_url=AZURE_OPENAI_ENDPOINT
    )

    return jsonify({"response": response["choices"][0]["message"]["content"]})

def calculate_strengths_weaknesses(reviews):
    category_counts = {key: {"positive": 0, "negative": 0} for key in CATEGORY_KEYWORDS}

    for review in reviews:
        sentiment = sentiment_analyzer(review["text"])[0]
        categories = categorize_review(review["text"])

        for category, count in categories.items():
            if count > 0:
                if sentiment["label"] == "POSITIVE":
                    category_counts[category]["positive"] += 1
                else:
                    category_counts[category]["negative"] += 1

    strengths = {}
    weaknesses = {}

    for category, counts in category_counts.items():
        total = counts["positive"] + counts["negative"]
        if total > 0:
            positive_percentage = round((counts["positive"] / total) * 100, 1)
            negative_percentage = round((counts["negative"] / total) * 100, 1)

            if positive_percentage > 60:
                strengths[category] = positive_percentage
            elif negative_percentage > 40:
                weaknesses[category] = negative_percentage

    return {"strengths": strengths, "weaknesses": weaknesses}

def calculate_restaurant_rank(place_id):
    """Get review count and revenue-based ranking"""
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,user_ratings_total,price_level&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url).json()
    
    total_reviews = response["result"].get("user_ratings_total", 0)
    price_level = response["result"].get("price_level", 2)  # Default to mid-range
    
    # Simulated revenue calculation (adjust this with real data)
    min_revenue = total_reviews * 20 * price_level
    max_revenue = total_reviews * 50 * price_level
    avg_revenue = (min_revenue + max_revenue) / 2

    # Simulated category-based ranking (mock logic)
    rank_category = "Mid-Tier"
    if avg_revenue > 1000000:
        rank_category = "Premium"
    elif avg_revenue > 500000:
        rank_category = "Upper-Mid"
    elif avg_revenue < 100000:
        rank_category = "Budget"

    return {
        "reviews": total_reviews,
        "min_revenue": min_revenue,
        "max_revenue": max_revenue,
        "avg_revenue": avg_revenue,
        "rank_category": rank_category
    }



