from mongodb import get_db
from datetime import datetime
import os
import dotenv

import face_recognition
import numpy as np

dotenv.load_dotenv()

def recognize(image_path, known_encodings, known_emails, tolerance=0.5) -> tuple[str, str | None]:
    image = face_recognition.load_image_file(image_path)
    encs = face_recognition.face_encodings(image)

    if not encs:
        return "No Face", None

    face = encs[0]
    matches = face_recognition.compare_faces(known_encodings, face, tolerance=tolerance)
    distances = face_recognition.face_distance(known_encodings, face)

    print("✅ Matches:", matches)
    print("📏 Distances:", distances.tolist())

    if True in matches:
        best_match_index = np.argmin(distances)
        email = known_emails[best_match_index]
        return "Recognized", email

    return "Unknown", None

def recognize_and_mark_attendance(image_path) -> dict:
    try:
        start_time = datetime.strptime(os.getenv("START_TIME"), "%H:%M").time()
        end_time = datetime.strptime(os.getenv("END_TIME"), "%H:%M").time()
        current_time = datetime.now().time()

        if current_time < start_time or current_time > end_time:
            return {"status": "error", "message": "Attendance is not open at this time"}

        db = get_db()
        users = list(db.users.find({}))

        known_encodings = [np.array(u["faceprint"], dtype=np.float64) for u in users]
        known_emails = [u["email"] for u in users]

        result, email = recognize(image_path, known_encodings, known_emails)

        if result == "No Face":
            return {"status": "error", "message": "No Face Detected"}
        if result == "Unknown":
            return {"status": "error", "message": "Unknown Face"}

        today = datetime.now().strftime("%Y-%m-%d")
        already = db.attendance.find_one({"email": email, "date": today})
        if already:
            return {"status": "error", "message": "Attendance Already Recorded"}

        db.attendance.insert_one({
            "email": email,
            "date": today,
            "time": datetime.now().strftime("%H:%M:%S")
        })

        return {"status": "success", "message": f"Attendance marked for {email}"}

    except Exception as e:
        return {"status": "error", "message": f"Server error: {str(e)}"}
