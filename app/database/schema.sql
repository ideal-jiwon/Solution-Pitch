CREATE TABLE IF NOT EXISTS review_analysis (
    id SERIAL PRIMARY KEY,
    review_id VARCHAR(255) UNIQUE NOT NULL REFERENCES cleaned_reviews(review_id),
    category VARCHAR(50),  -- 감성 분석 결과 (positive, negative, neutral)
    sentiment_score FLOAT,  -- 긍정 점수 (Azure API에서 제공)
    keywords TEXT[],  -- 주요 키워드 리스트
    summary TEXT,  -- 요약된 내용
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
