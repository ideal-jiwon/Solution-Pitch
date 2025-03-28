from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

photo_bp = Blueprint("photo", __name__) 

from app.image_analysis import compare_with_pexels

@photo_bp.route("/upload_photo", methods=["POST"])
def upload_photo():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image uploaded"}), 400

        filename = secure_filename(file.filename)
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        print("✅ Image saved:", filepath)

        
        from app.image_analysis import compare_with_pexels
        matches, solution = compare_with_pexels(filepath)

        print("✅ Matches:", matches)
        print("✅ Solution:", solution)

        return jsonify({
            "message": "Complete!",
            "matches": matches,
            "solution": solution
        })

    except Exception as e:
        print("❌ Error in upload_photo:", str(e)) 
        return jsonify({"error": str(e)}), 500

