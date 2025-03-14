import requests
import os

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
TEXT_ANALYTICS_ENDPOINT = os.getenv("TEXT_ANALYTICS_ENDPOINT")

HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_OPENAI_API_KEY,
    "Content-Type": "application/json"
}

def analyze_sentiment(text):
    """Azure API를 사용하여 감성 분석 수행"""
    url = f"{TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/sentiment"
    data = {"documents": [{"id": "1", "text": text}]}

    response = requests.post(url, headers=HEADERS, json=data)
    result = response.json()

    if "documents" in result:
        sentiment_data = result["documents"][0]
        return sentiment_data["sentiment"], sentiment_data["confidenceScores"]
    return "neutral", {"positive": 0.5, "negative": 0.5, "neutral": 0.5}  # 기본값

def extract_key_phrases(text):
    """Azure API를 사용하여 주요 키워드 추출"""
    url = f"{TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/keyPhrases"
    data = {"documents": [{"id": "1", "text": text}]}

    response = requests.post(url, headers=HEADERS, json=data)
    result = response.json()

    if "documents" in result:
        return result["documents"][0].get("keyPhrases", [])
    return []

def summarize_text(text):
    """Azure API를 사용하여 요약 생성"""
    url = f"{TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/summarize"
    data = {"documents": [{"id": "1", "text": text, "sentenceCount": 2}]}

    response = requests.post(url, headers=HEADERS, json=data)
    result = response.json()

    if "documents" in result:
        return " ".join(result["documents"][0].get("sentences", []))
    return text[:200]  # 기본적으로 200자만 유지




