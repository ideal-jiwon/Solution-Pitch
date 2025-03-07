from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

def create_app():
    """Flask 앱 생성 및 초기화"""
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    # 환경변수 로드
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
    app.config["GOOGLE_REDIRECT_URI"] = os.getenv("GOOGLE_REDIRECT_URI")
    app.config["GOOGLE_PLACES_API_KEY"] = os.getenv("GOOGLE_PLACES_API_KEY")
    app.config["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    app.config["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")

    # 블루프린트 등록
    from app.routes import main_bp
    from app.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app


