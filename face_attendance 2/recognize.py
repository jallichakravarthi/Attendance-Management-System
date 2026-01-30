from mongodb import get_db
from datetime import datetime, timedelta
import os
import dotenv

import face_recognition
import numpy as np

dotenv.load_dotenv()

def recognize(image_path, known_encodings, known_regNos, tolerance=0.5) -> tuple[str, str | None]:
    image = face_recognition.load_image_file(image_path)
    encs = face_recognition.face_encodings(image)

    if not encs:
        return "No Face", None

    if not known_encodings:
        return "Unknown", None

    face = encs[0].astype(np.float64)

    matches = face_recognition.compare_faces(
        known_encodings,
        face,
        tolerance=tolerance
    )
    distances = face_recognition.face_distance(known_encodings, face)

    print("✅ Matches:", matches)
    print("📏 Distances:", distances.tolist())

    if True in matches:
        best_match_index = np.argmin(distances)
        regNo = known_regNos[best_match_index]
        return "Recognized", regNo

    return "Unknown", None



from mongodb import get_db
from datetime import datetime, timedelta
import os
import dotenv
import face_recognition
import numpy as np

dotenv.load_dotenv()

def recognize_and_mark_attendance(image_path) -> dict:
    try:
        start_time = datetime.strptime(os.getenv("START_TIME"), "%H:%M").time()
        end_time = datetime.strptime(os.getenv("END_TIME"), "%H:%M").time()
        current_time = datetime.now().time()

        if current_time < start_time or current_time > end_time:
            return {
                "status": "error",
                "message": "Attendance is not open at this time"
            }

        # ⏱️ Late cutoff (30 mins)
        start_dt = datetime.combine(datetime.today(), start_time)
        late_cutoff = (start_dt + timedelta(minutes=30)).time()

        attendance_status = (
            "present" if current_time <= late_cutoff else "late"
        )

        db = get_db()
        users = list(db.users.find({}))

        known_encodings = []
        known_regNos = []

        for u in users:
            faceprint = u.get("faceprint")
            regNo = u.get("regNo")

            if (
                isinstance(faceprint, list)
                and len(faceprint) > 0
                and regNo
            ):
                known_encodings.append(
                    np.array(faceprint, dtype=np.float64)
                )
                known_regNos.append(regNo)

        result, regNo = recognize(
            image_path,
            known_encodings,
            known_regNos
        )

        if result == "No Face":
            return {"status": "error", "message": "No Face Detected"}

        if result == "Unknown":
            return {"status": "error", "message": "Unknown Face"}

        today = datetime.now().strftime("%Y-%m-%d")

        already = db.attendance.find_one({
            "regNo": regNo,
            "date": today
        })

        if already:
            if already.get("status") in ["present", "late"]:
                return {
                    "status": "error",
                    "message": f"Attendance already marked as {already['status']}"
                }

            if already.get("status") == "absent":
                db.attendance.update_one(
                    {"_id": already["_id"]},
                    {
                        "$set": {
                            "status": attendance_status,
                            "time": datetime.now().strftime("%H:%M:%S")
                        }
                    }
                )
                return {
                    "status": "success",
                    "message": f"Attendance updated to {attendance_status} for {regNo}"
                }

        db.attendance.insert_one({
            "regNo": regNo,
            "date": today,
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": attendance_status
        })

        return {
            "status": "success",
            "message": f"Attendance marked as {attendance_status} for {regNo}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Server error: {str(e)}"
        }
