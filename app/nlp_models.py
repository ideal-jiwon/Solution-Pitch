from transformers import pipeline
import requests
import os

# 감정 분석 모델 로드
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

def analyze_sentiment(text):
    """리뷰 감정 분석 수행"""
    sentiment = sentiment_analyzer(text)[0]
    return sentiment["label"], sentiment["score"]

def categorize_review(text):
    """리뷰를 서비스, 가격, 메뉴, 위치, 분위기 기준으로 분류"""
    categories = {key: 0 for key in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text.lower():
                categories[category] += 1  # 해당 카테고리의 점수 증가

    return categories

def fetch_reviews(place_id):
    """Google Places API에서 리뷰를 가져오고 감정 분석 및 카테고리 분류 수행"""
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,reviews&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "reviews" not in data.get("result", {}):
        return {"error": "No reviews found"}

    reviews = data["result"]["reviews"]
    category_scores = {key: [] for key in CATEGORY_KEYWORDS}

    processed_reviews = []
    for review in reviews:
        sentiment, confidence = analyze_sentiment(review["text"])
        categories = categorize_review(review["text"])

        # 감정 점수를 별점(1~5점)으로 변환
        score = round(confidence * 5)

        for category, count in categories.items():
            if count > 0:
                category_scores[category].append(score)

        processed_reviews.append({
            "author": review["author_name"],
            "rating": review["rating"],
            "text": review["text"],
            "time": review["relative_time_description"],
            "sentiment": sentiment,
            "confidence": confidence,
            "categories": categories
        })

    # 각 카테고리별 평균 점수 계산
    avg_scores = {category: round(sum(scores) / len(scores), 1) if scores else "-" for category, scores in category_scores.items()}

    return {"reviews": processed_reviews, "avg_scores": avg_scores}

def analyze_review_relationships(reviews):
    """Azure OpenAI를 사용하여 리뷰 간 관계 분석"""
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

    review_texts = "\n".join([review["text"] for review in reviews])
    
    prompt = f"""
    Analyze the following restaurant reviews and identify key relationships between service, price, menu, location, and ambiance.
    Provide insights on patterns, correlations, and potential improvements:
    {review_texts}
    """

    response = requests.post(
        f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-4/chat/completions",
        headers={"Authorization": f"Bearer {AZURE_OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={"messages": [{"role": "system", "content": prompt}]}
    ).json()

    return response["choices"][0]["message"]["content"]
