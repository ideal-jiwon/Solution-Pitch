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
            return jsonify({"response": "✏️ 메모할 내용을 입력해주세요!"})

        # Apple Reminders에 추가
        script = f'''
        tell application "Reminders"
            tell list "Reminders"
                make new reminder with properties {{name:"{note}"}}
            end tell
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
            return jsonify({"response": f"✅ 알림에 저장했어요: {note}"})
        except subprocess.CalledProcessError as e:
            return jsonify({"response": "❌ 알림 저장에 실패했어요."}), 500

    # 일반 응답
    return jsonify({
        "response": "👋 안녕하세요! 'remind: ~' 형식으로 메모를 남기면 알림으로 저장해드려요."
    })
