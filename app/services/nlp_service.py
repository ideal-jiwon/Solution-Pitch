import requests
import os

# 🔹 환경변수에서 API 키와 엔드포인트 불러오기
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
TEXT_ANALYTICS_ENDPOINT = os.getenv("TEXT_ANALYTICS_ENDPOINT")

# 🔸 경고 출력
if not AZURE_OPENAI_API_KEY or not TEXT_ANALYTICS_ENDPOINT:
    print("❌ API 키나 엔드포인트가 설정되지 않았습니다. .env 파일 확인!")

# 🔹 공통 헤더
HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_OPENAI_API_KEY,
    "Content-Type": "application/json"
}

def classify_category(text):
    """ 키워드 기반으로 간단한 카테고리 분류 """
    text = text.lower()

    keywords = {
        "taste": ["taste", "tasty", "flavor", "sweet", "spicy", "bland", "fresh"],
        "price": ["price", "cheap", "expensive", "affordable", "value"],
        "service": ["service", "friendly", "rude", "staff", "attentive"],
        "cleanliness": ["clean", "dirty", "hygiene", "sanitary"],
        "atmosphere": ["atmosphere", "vibe", "lighting", "music", "interior"],
        "speed": ["slow", "fast", "wait", "waiting", "quick"],
    }

    for category, words in keywords.items():
        if any(word in text for word in words):
            return category
    return "other"

def analyze_sentiment(text):
    """ Azure API를 사용한 감성 분석 """
    url = f"{TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/sentiment"
    data = {"documents": [{"id": "1", "text": text}]}

    try:
        response = requests.post(url, headers=HEADERS, json=data)
        result = response.json()
        print("🔍 Sentiment Response:", result)

        if "documents" in result and result["documents"]:
            sentiment_data = result["documents"][0]
            return sentiment_data["sentiment"], sentiment_data["confidenceScores"]
        else:
            print("❌ 감성 분석 결과 없음:", result)
    except Exception as e:
        print(f"❌ 감성 분석 실패: {e}")

    return "neutral", {"positive": 0.5, "negative": 0.5, "neutral": 0.5}

def extract_key_phrases(text):
    """ Azure API를 사용한 키워드 추출 """
    url = f"{TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/keyPhrases"
    data = {"documents": [{"id": "1", "text": text}]}

    try:
        response = requests.post(url, headers=HEADERS, json=data)
        result = response.json()
        print("🔍 KeyPhrase Response:", result)

        if "documents" in result and result["documents"]:
            return result["documents"][0].get("keyPhrases", [])
        else:
            print("❌ 키워드 추출 결과 없음:", result)
    except Exception as e:
        print(f"❌ 키워드 추출 실패: {e}")

    return []





