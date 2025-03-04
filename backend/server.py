import openai
from flask import Flask, request, jsonify
import requests
from transformers import pipeline

app = Flask(__name__)

GOOGLE_PLACES_API_KEY = "AIzaSyCcqraspdA5PdAI6mZQTElHBEkDRK0KY5A"
AZURE_OPENAI_API_KEY="AmO7fs6GbfsDFwi2KFcTTZILxclkljZxsEhprX03xHb7TfMlxfMaJQQJ99BCACYeBjFXJ3w3AAABACOG6JA0"
AZURE_OPENAI_ENDPOINT = "https://azure-services-openai.openai.azure.com/"


# 감정 분석 모델 로드 (Hugging Face 모델 사용)
sentiment_analyzer = pipeline("sentiment-analysis")

# 🔹 서비스, 가격, 메뉴, 위치, 분위기 관련 키워드 목록
CATEGORY_KEYWORDS = {
    "service": ["staff", "waiter", "service", "customer service", "friendly", "rude", "slow", "fast"],
    "price": ["price", "expensive", "cheap", "affordable", "cost", "worth", "overpriced"],
    "menu": ["food", "menu", "dish", "drink", "taste", "flavor", "meal", "delicious"],
    "location": ["location", "parking", "near", "far", "convenient", "access"],
    "ambiance": ["atmosphere", "ambiance", "vibe", "music", "decor", "cozy", "loud", "quiet"]
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
    """프론트엔드에서 요청을 받아 리뷰 데이터를 반환한다."""
    place_id = request.args.get("place_id")
    if not place_id:
        return jsonify({"error": "Missing place_id"}), 400

    result = fetch_reviews(place_id)
    result["relationship_analysis"] = analyze_review_relationships(result["reviews"])
    
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




