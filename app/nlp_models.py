from transformers import pipeline
import openai
import os

# 감정 분석 모델 로드
sentiment_analyzer = pipeline("sentiment-analysis")

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
    categories = {key: 0 for key in CATEGORY_KEYWORDS}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text.lower():
                categories[category] += 1

    return categories

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
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    return response["choices"][0]["message"]["content"]


