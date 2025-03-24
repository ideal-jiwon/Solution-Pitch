from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import psycopg2
import os

# PostgreSQL 연결 설정
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def connect_db():
    """PostgreSQL 데이터베이스 연결"""
    return psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)

def insert_review_raw(place_id, review_id, text, rating):
    """Raw 리뷰 데이터를 PostgreSQL에 저장"""
    conn = connect_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO raw_reviews (place_id, review_id, review_text, rating)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (review_id) DO NOTHING;
    """
    cursor.execute(insert_query, (place_id, review_id, text, rating))

    conn.commit()
    cursor.close()
    conn.close()

def scrape_reviews(place_id):
    """주어진 place_id로 Google Maps 리뷰를 크롤링하고 PostgreSQL에 저장"""
    reviews_list = []

    # Chrome WebDriver 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.177 Safari/537.36")


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # 📌 Google Maps 리뷰 페이지 URL 생성
    google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    driver.get(google_maps_url)

    time.sleep(5)  # 페이지 로딩 대기

    try:
        reviews = driver.find_elements(By.CLASS_NAME, "wiI7pd")  # 리뷰 텍스트
        ratings = driver.find_elements(By.CLASS_NAME, "kvMYJc")  # 별점

        for i in range(min(len(reviews), 10)):  # 최대 10개 리뷰 크롤링
            review_text = reviews[i].text
            rating_value = ratings[i].get_attribute("aria-label")  # "Rated 4.0 out of 5" 형태

            review_id = f"{place_id}_{i}"
            reviews_list.append({"review_id": review_id, "text": review_text, "rating": rating_value})

            # 📌 PostgreSQL에 저장
            insert_review_raw(place_id, review_id, review_text, rating_value)

    except Exception as e:
        print("❌ Error during scraping:", e)

    driver.quit()
    return reviews_list
