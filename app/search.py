from flask import Blueprint, request, jsonify
from app.services.db import connect_db

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["POST"])
def search():
    data = request.json
    name = data.get("name", "").strip()
    address = data.get("address", "").strip()
    city = data.get("city", "").strip()
    state = data.get("state", "").strip()
    postal_code = data.get("postal_code", "").strip()

    if not all([name, address, city, state, postal_code]):
        return jsonify({"error": "Incomplete business info"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT business_id, name, address, city, latitude, longitude
        FROM businesses
        WHERE LOWER(name) = LOWER(%s)
          AND LOWER(address) = LOWER(%s)
          AND LOWER(city) = LOWER(%s)
          AND LOWER(state) = LOWER(%s)
          AND postal_code = %s
        LIMIT 1;
    """
    cursor.execute(query, (name, address, city, state, postal_code))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return jsonify({"error": "Business not found"}), 404

    business_id, name, address, city, lat, lng = row
    return jsonify({
        "business_id": business_id,
        "name": name,
        "address": address,
        "city": city,
        "coordinates": { "latitude": lat, "longitude": lng }
    })
