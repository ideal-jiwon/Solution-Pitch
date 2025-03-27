from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import subprocess

remind_bp = Blueprint("remind", __name__)

@remind_bp.route("/remind", methods=["POST"])
def remind():
    data = request.json
    note = data.get("note", "").strip()
    if not note:
        return jsonify({"error": "✏️ 메모할 내용을 입력해주세요!"}), 400

    # 🔔 알림 시간 설정: 지금으로부터 15초 후 (아이폰에 푸시 알림 뜨게 하기 위해 필요)
    reminder_time = (datetime.now() + timedelta(seconds=15)).strftime("%B %d, %Y %I:%M %p")

    # AppleScript로 알림 등록
    script = f'''
    tell application "Reminders"
        tell list "Reminders"
            make new reminder with properties {{name:"{note}", remind me date:date "{reminder_time}"}}
        end tell
    end tell
    '''

    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return jsonify({"message": f"✅ 알림에 저장했어요: {note}\n🔔 잠시 후 iPhone에도 알림이 울릴 거예요!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "❌ 알림 저장에 실패했어요."}), 500
