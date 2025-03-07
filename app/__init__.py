from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.routes import setup_routes

# 환경 변수 로드
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # CORS 설정

    # 라우트 등록
    setup_routes(app)

    return app
