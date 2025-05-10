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

# 
load_dotenv()

# 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "..", "public")

#
app = Flask(__name__)
CORS(app)

#
app.register_blueprint(places_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(models_bp, url_prefix="/models")
app.register_blueprint(chat_bp)
app.register_blueprint(remind_bp)
app.register_blueprint(photo_bp, url_prefix="/photo")
app.register_blueprint(search_bp)

#
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

#
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(PUBLIC_DIR, path)

print("Flask server launched!")

if os.getenv("SEED_ON_STARTUP", "false").lower() == "true":
    try:
        from insert_all import insert_all, analyze_and_update_reviews
        print("🌱 Starting initial data insert & analysis...")
        insert_all()
        analyze_and_update_reviews()
        print("✅ Initial data insert complete.")
    except Exception as e:
        print(f"❌ Failed to seed data on startup: {e}")
