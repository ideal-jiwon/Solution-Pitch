from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.routes import places_bp
from app.auth import auth_bp
from app.models import models_bp
from app.chat import chat_bp
from app.remind import remind_bp
from app.photo import photo_bp
from app.search import search_bp

# 🔹 환경 변수 로드
load_dotenv()

# 🔹 현재 프로젝트 경로
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "..", "public")

# 🔹 Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 🔹 블루프린트 등록
app.register_blueprint(places_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(models_bp, url_prefix="/models")
app.register_blueprint(chat_bp)
app.register_blueprint(remind_bp)
app.register_blueprint(photo_bp, url_prefix="/photo")
app.register_blueprint(search_bp)

# 🔹 기본 페이지 제공
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

# 🔹 정적 파일 제공
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(PUBLIC_DIR, path)

print("Flask server launched!")
