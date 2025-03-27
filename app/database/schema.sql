-- Business 테이블
CREATE TABLE IF NOT EXISTS businesses (
    business_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(255),
    postal_code VARCHAR(20),
    latitude FLOAT,
    longitude FLOAT,
    categories TEXT,  -- 기존 TEXT[] → TEXT로 변경
    hours JSONB,      -- 운영시간을 JSON 형태로 저장
    review_count INTEGER,
    stars FLOAT,
    is_open BOOLEAN
);

-- Review 테이블
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(255) PRIMARY KEY,
    business_id VARCHAR(255) REFERENCES businesses(business_id),
    stars INTEGER,
    date DATE,
    text TEXT,
    useful INTEGER,
    funny INTEGER,
    cool INTEGER,
    place_id VARCHAR(255)
);


