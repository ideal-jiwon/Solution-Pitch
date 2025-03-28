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
    model = get_model()
    image = Image.open(path).convert("RGB")
    return model.encode(image, convert_to_tensor=True)

def fetch_popular_pexels_images(query="cafe", per_page=6):
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    headers = { "Authorization": PEXELS_API_KEY }
    params = { "query": query, "per_page": per_page }

    res = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    
    print("🔍 Pexels status:", res.status_code)
    print("🔍 Pexels response:", res.json())

    photos = res.json().get("photos", [])
    return [photo["src"]["medium"] for photo in photos]


def compare_with_pexels(uploaded_path):
    target_embedding = get_image_embedding_from_path(uploaded_path)
    pexels_images = fetch_popular_pexels_images()

    if not pexels_images:
        return [], "❌ We could not find any references in Pexels"

    scores = []
    for url in pexels_images:
        emb = get_image_embedding_from_url(url)
        sim = util.cos_sim(target_embedding, emb).item()
        scores.append((url, sim))

    best = sorted(scores, key=lambda x: -x[1])
    if not best:
        return [], "❌ We failed analysing photos"

    return best[:3], generate_solution(best[0][1])

    
def generate_solution(similarity_score):
    if similarity_score > 0.9:
        return "Your photo is very simliar to popular photos in Social Media"
    elif similarity_score > 0.75:
        return "Why don't you work on lighting and angles? See our references"
    else:
        return "Photos are too dark. Try uploading photos with natural sunlight or vivid"
    
def compare_with_pexels(uploaded_path, query="restaurant"):
    target_embedding = get_image_embedding_from_path(uploaded_path)
    pexels_images = fetch_popular_pexels_images(query)

    if not pexels_images:
        return [], "❌ We could not find any references in Pexels"

    scores = []
    for url in pexels_images:
        emb = get_image_embedding_from_url(url)
        sim = util.cos_sim(target_embedding, emb).item()
        scores.append((url, sim))

    best = sorted(scores, key=lambda x: -x[1])
    
    # 🔐 안전하게 처리
    if not best:
        return [], "❌ We failed to analyze photos"

    return best[:3], generate_solution(best[0][1])

