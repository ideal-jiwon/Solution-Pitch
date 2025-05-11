from flask import Blueprint, request, jsonify
import subprocess

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").strip()

    if message.lower().startswith("remind:"):
        note = message[7:].strip()
        if not note:
            return jsonify({"response": "✏️ Please make a note here!"})

        script = f'''
        tell application "Reminders"
            tell list "Reminders"
                make new reminder with properties {{name:"{note}"}}
            end tell
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return jsonify({"response": f"Alert saved: {note}"})
        except subprocess.CalledProcessError as e:
            return jsonify({"response": "❌ Alert save failed"}), 500

    return jsonify({
        "response": "👋 Hi! make a note starting with 'remind: ~' It will be saved in your Apple Reminder"
    })
