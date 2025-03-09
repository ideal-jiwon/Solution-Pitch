from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

# 🔹 블루프린트 가져오기
from app.routes import places_bp
from app.auth import auth_bp
from app.models import models_bp  # 📌 models.py 블루프린트 추가

# 🔹 환경 변수 로드
load_dotenv()

# 🔹 현재 `server.py`의 경로를 기준으로 `public/` 폴더의 절대 경로 찾기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")  # public 폴더 설정

# 🔹 Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 🔹 블루프린트 등록
app.register_blueprint(places_bp, url_prefix="/api")  # 장소 검색
app.register_blueprint(auth_bp, url_prefix="/auth")   # 로그인 & 인증
app.register_blueprint(models_bp, url_prefix="/models")  # 📌 리뷰 분석 엔드포인트 등록

# 🔹 기본 페이지 제공 (index.html)
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

# 🔹 정적 파일 제공 (CSS, JS, 이미지 등)
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(PUBLIC_DIR, path)

# 📌 기존의 `@app.route("/analyze_reviews")` 삭제 (models.py에 이미 있음)

# 📌 디버깅 로그 추가
logging.basicConfig(level=logging.DEBUG)
print("DEBUG: PUBLIC_DIR =", PUBLIC_DIR)
print("DEBUG: Does PUBLIC_DIR exist?", os.path.exists(PUBLIC_DIR))
print("DEBUG: PUBLIC_DIR contents:", os.listdir(PUBLIC_DIR) if os.path.exists(PUBLIC_DIR) else "Directory not found")
