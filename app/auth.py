from flask import Blueprint, request, jsonify, session, redirect
import requests
import os


# 🔹 블루프린트 생성
auth_bp = Blueprint("auth", __name__)

# 🔹 Google OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


# 🔹 Google 로그인 URL 생성
@auth_bp.route("/login")
def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        "&redirect_uri=" + GOOGLE_REDIRECT_URI +
        "&scope=openid%20email%20profile"
    )
    return jsonify({"auth_url": google_auth_url})

# 🔹 Google 로그인 콜백 처리
@auth_bp.route("/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No authorization code provided"}), 400

    # 🔹 Access Token 요청
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    token_info = token_response.json()

    if "access_token" not in token_info:
        return jsonify({"error": "Failed to obtain access token"}), 400

    access_token = token_info["access_token"]

    # 🔹 Google 사용자 정보 요청
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(userinfo_url, headers=headers)
    user_info = userinfo_response.json()

    # 세션에 사용자 정보 저장
    session["user"] = user_info

    return redirect("http://localhost:5500/home.html")  # 로그인 성공 후 리디렉션

# 🔹 사용자 정보 가져오기
@auth_bp.route("/auth/user", methods=["GET"])
def get_user():
    if "user" in session:
        return jsonify(session["user"])
    return jsonify({"error": "User not logged in"}), 401

# 🔹 로그아웃
@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    auth_bp.run(debug=True)