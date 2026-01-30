from mongodb import get_db
from datetime import datetime
import os
import dotenv

dotenv.load_dotenv()

def mark_absentees_if_window_closed():
    db = get_db()

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().time()
    end_time = datetime.strptime(os.getenv("END_TIME"), "%H:%M").time()

    # ⏳ Attendance window still open
    if current_time <= end_time:
        print("⏳ Attendance window still open or not open yet, skipping absentee marking")
        return {
            "status": "skipped",
            "message": "Attendance window still open"
        }

    # ✅ All valid users (students + faculty) with regNo
    users = db.users.find(
        {
            "role": {"$in": ["Student", "Faculty"]},
            "isValid": True,
            "regNo": {"$exists": True}
        },
        {"regNo": 1}
    )

    all_regNos = {u["regNo"] for u in users}

    # 🟢 Already marked today
    marked = db.attendance.find(
        {"date": today},
        {"regNo": 1}
    )
    marked_regNos = {m["regNo"] for m in marked}

    # ❌ Absentees
    absentees = all_regNos - marked_regNos

    if not absentees:
        return {
            "status": "success",
            "message": "No absentees to mark"
        }

    now_time = datetime.now().strftime("%H:%M:%S")

    docs = [
        {
            "regNo": regNo,
            "date": today,
            "time": now_time,      # ✅ REQUIRED
            "status": "absent"
        }
        for regNo in absentees
    ]

    try:
        db.attendance.insert_many(docs, ordered=False)
    except Exception:
        pass  # Ignore duplicates safely

    return {
        "status": "success",
        "message": f"Marked {len(absentees)} absentees (students + faculty)"
    }
