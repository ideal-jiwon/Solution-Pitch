from flask import Blueprint, request, jsonify
from app.services.db import connect_db

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["POST"])
def search():
    data = request.json
    full_address = data.get("full_address","").strip()

    if not full_address:
        return jsonify({"error": "Missing address"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT business_id, name, address, city, latitude, longitude
        FROM businesses
        WHERE LOWER(address || ', ' || city || ', ' || state || ' ' || postal_code) LIKE LOWER(%s)
        LIMIT 1;
    """
    cursor.execute(query, (f"%{full_address}%",))
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


@search_bp.route("/api/address-suggestions", methods=["GET"])
def suggest_address():
    query = request.args.get("query","").strip()
    if not query:
        return jsonify([])
    
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT address || ', ' || city || ', ' || state || ' ' || postal_code AS full_address
        FROM businesses
        WHERE LOWER(address || ', ' || city || ', ' || state || ' ' || postal_code) LIKE LOWER(%s)
        LIMIT 10
    """, (f"%{query}%",))

    suggestions = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(suggestions)

