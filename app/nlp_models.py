from transformers import pipeline

# 감정 분석 모델 로드
sentiment_analyzer = pipeline("sentiment-analysis")

# 리뷰를 분석하여 긍정/부정 감정을 판단하는 함수
def analyze_sentiment(text):
    sentiment = sentiment_analyzer(text)[0]
    return sentiment["label"], sentiment["score"]
