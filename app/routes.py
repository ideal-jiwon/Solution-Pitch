from flask import Blueprint, request, jsonify
import requests
import os
places_bp = Blueprint("places", __name__)


# Google Places API Key
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Google Places API v1 searchText URL
PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

@places_bp.route("/places/search", methods=["POST"])
def search_places():
    """Google Places API - searchText 방식으로 장소 검색"""
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
         "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location"
    }
    
    payload = {
        "textQuery": query
    }

    response = requests.post(PLACES_SEARCH_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data", "details": response.text}), response.status_code

    return jsonify(response.json())
