import face_recognition
from mongodb import get_db
from recognize import recognize
import numpy as np

def register_face_to_db(image_path, regNo) -> dict:
    db = get_db()

    # Normalize regNo
    regNo = regNo.upper().strip()

    # Step 1: Check if user with given regNo exists
    user = db.users.find_one({"regNo": regNo})
    if not user:
        print(f"❌ No user found with regNo: {regNo}")
        return {
            "status": "error",
            "message": f"No user found with regNo: {regNo}"
        }

    # Step 2: Check if face already registered
    faceprint = user.get("faceprint")
    if isinstance(faceprint, list) and len(faceprint) > 0:
        print(f"❌ Face already registered for {regNo}")
        return {
            "status": "error",
            "message": f"Face already registered for {regNo}"
        }

    # Step 3: Load existing users with faceprints (exclude current regNo)
    users = list(db.users.find({
        "faceprint": {"$exists": True, "$ne": []},
        "regNo": {"$ne": regNo}
    }))

    known_encodings = []
    known_regNos = []

    for u in users:
        u_faceprint = u.get("faceprint")
        if isinstance(u_faceprint, list) and len(u_faceprint) > 0:
            known_encodings.append(
                np.array(u_faceprint, dtype=np.float64)
            )
            known_regNos.append(u.get("regNo"))

    # Step 4: Check for duplicate face
    result, matched_regNo = recognize(
        image_path,
        known_encodings,
        known_regNos
    )

    if result != "Unknown" and matched_regNo is not None:
        print(f"❌ Face already registered as {matched_regNo}")
        return {
            "status": "error",
            "message": f"Face already registered as {matched_regNo}"
        }

    # Step 5: Encode new face
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        print("❌ No face found in the image")
        return {
            "status": "error",
            "message": "No face found in the image"
        }

    faceprint = encodings[0].astype(np.float64).tolist()

    # Step 6: Save faceprint
    db.users.update_one(
        {"regNo": regNo},
        {"$set": {"faceprint": faceprint}}
    )

    print(f"✅ Face registered for {regNo}")
    return {
        "status": "success",
        "message": f"Face registered for {regNo}"
    }
