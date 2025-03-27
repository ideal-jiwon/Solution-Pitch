import requests
from PIL import Image
from io import BytesIO
import torch
import os
from sentence_transformers import SentenceTransformer, util

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('clip-ViT-B-32')
    return _model


def get_image_embedding_from_url(url):
    model = get_model()
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    return model.encode(image, convert_to_tensor=True)

def get_image_embedding_from_path(path):
    model = get_model()  # ✅ 이 줄 추가 필요
    image = Image.open(path).convert("RGB")
    return model.encode(image, convert_to_tensor=True)

def fetch_popular_pexels_images(query="cafe", per_page=6):
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    headers = { "Authorization": PEXELS_API_KEY }
    params = { "query": query, "per_page": per_page }

    res = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    
    # 🔍 로그 찍기
    print("🔍 Pexels status:", res.status_code)
    print("🔍 Pexels response:", res.json())

    photos = res.json().get("photos", [])
    return [photo["src"]["medium"] for photo in photos]


def compare_with_pexels(uploaded_path):
    target_embedding = get_image_embedding_from_path(uploaded_path)
    pexels_images = fetch_popular_pexels_images()  # ⬅️ query 없이 기본값 사용

    if not pexels_images:
        return [], "❌ Pexels에서 유사 이미지를 찾을 수 없었어요."

    scores = []
    for url in pexels_images:
        emb = get_image_embedding_from_url(url)
        sim = util.cos_sim(target_embedding, emb).item()
        scores.append((url, sim))

    best = sorted(scores, key=lambda x: -x[1])
    if not best:
        return [], "❌ 유사 이미지를 분석하는 데 실패했어요."

    return best[:3], generate_solution(best[0][1])

    
def generate_solution(similarity_score):
    if similarity_score > 0.9:
        return "사진 퀄리티가 매우 높아요! 그대로 유지하세요 👏"
    elif similarity_score > 0.75:
        return "조명/구도를 조금 더 개선하면 더 눈에 띌 수 있어요 💡"
    else:
        return "사진이 어두워 보일 수 있어요. 자연광 또는 더 선명한 사진을 시도해보세요 📸"
    
def compare_with_pexels(uploaded_path, query="cafe"):
    target_embedding = get_image_embedding_from_path(uploaded_path)
    pexels_images = fetch_popular_pexels_images(query)

    if not pexels_images:
        return [], "❌ Pexels에서 유사 이미지를 찾을 수 없었어요. 검색어를 바꿔보세요!"

    scores = []
    for url in pexels_images:
        emb = get_image_embedding_from_url(url)
        sim = util.cos_sim(target_embedding, emb).item()
        scores.append((url, sim))

    best = sorted(scores, key=lambda x: -x[1])
    
    # 🔐 안전하게 처리
    if not best:
        return [], "❌ 유사 이미지를 분석하는 데 실패했어요."

    return best[:3], generate_solution(best[0][1])

