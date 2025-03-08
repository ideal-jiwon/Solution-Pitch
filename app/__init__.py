from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory

# 🔹 환경 변수 로드
load_dotenv()

# 🔹 현재 `server.py`의 경로를 기준으로 `public/` 폴더의 절대 경로 찾기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 한 번만 dirname() 사용
PUBLIC_DIR = os.path.join(BASE_DIR, "public")  # public 폴더 설정

# Flask App Creation

app = Flask(__name__)
CORS(app)

# 🔹 기본 페이지 제공 (index.html)
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

# 🔹 정적 파일 제공 (CSS, JS, 이미지 등)
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(PUBLIC_DIR, path)

# 🔹 블루프린트 등록 (auth.py, models.py에서 가져옴)
from app.auth import auth_bp
from app.models import models_bp

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(models_bp, url_prefix="/models")

print("DEBUG: PUBLIC_DIR =", PUBLIC_DIR)
print("DEBUG: Does PUBLIC_DIR exist?", os.path.exists(PUBLIC_DIR))
print("DEBUG: PUBLIC_DIR contents:", os.listdir(PUBLIC_DIR) if os.path.exists(PUBLIC_DIR) else "Directory not found")
