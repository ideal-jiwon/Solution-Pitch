from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory
from app.routes import places_bp
from app.auth import auth_bp
from app.models import models_bp
from app.services.db import connect_db, create_tables

# 🔹 환경 변수 로드
load_dotenv()

# 🔹 현재 프로젝트
BASE_DIR = (os.path.abspath(os.path.dirname(__file__)))
print(f"DEBUG: BASE_DIR = {BASE_DIR}")
PUBLIC_DIR = os.path.join(BASE_DIR, "..", "public")

# Flask App Creation

app = Flask(__name__)
CORS(app)

# 🔹 블루프린트 등록
app.register_blueprint(places_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(models_bp, url_prefix="/models")

# 🔹 기본 페이지 제공 (index.html)
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

# 🔹 정적 파일 제공 (CSS, JS, 이미지 등)
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(PUBLIC_DIR, path)


print("DEBUG: PUBLIC_DIR =", PUBLIC_DIR)
print("DEBUG: Does PUBLIC_DIR exist?", os.path.exists(PUBLIC_DIR))
print("DEBUG: PUBLIC_DIR contents:", os.listdir(PUBLIC_DIR) if os.path.exists(PUBLIC_DIR) else "Directory not found")

# 🔹 PostgreSQL 테이블 생성
create_tables()