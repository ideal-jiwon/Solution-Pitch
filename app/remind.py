from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import subprocess

remind_bp = Blueprint("remind", __name__)

@remind_bp.route("/remind", methods=["POST"])
def remind():
    data = request.json
    note = data.get("note", "").strip()
    if not note:
        return jsonify({"error": "leave a note please"}), 400
    
    reminder_time = (datetime.now() + timedelta(seconds=15)).strftime("%B %d, %Y %I:%M %p")

    script = f'''
    tell application "Reminders"
        tell list "Reminders"
            make new reminder with properties {{name:"{note}", remind me date:date "{reminder_time}"}}
        end tell
    end tell
    '''

    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return jsonify({"message": f"Alert saved: {note}\n🔔 you will receive a notification soon"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed"}), 500
