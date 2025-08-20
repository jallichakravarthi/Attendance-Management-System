import face_recognition
from mongodb import get_db
from recognize import recognize
import numpy as np

def register_face_to_db(image_path, email) -> dict:
    db = get_db()

    # Step 1: Check if user with given email exists
    user = db.users.find_one({"email": email})
    if not user:
        print(f"❌ No user found with email: {email}")
        return {"status": "error", "message": f"No user found with email: {email}"}
    
    # Step 2: If faceprint already registered for this user
    if "faceprint" in user and user["faceprint"] is not None:
        print(f"❌ Face already registered for {email}")
        return {"status": "error", "message": f"Face already registered for {email}"}

    # Step 3: Load existing users with faceprints (excluding this email)
    users = list(db.users.find({"faceprint": {"$ne": None}, "email": {"$ne": email}}))
    known_encodings = [np.array(u["faceprint"], dtype=np.float64) for u in users]
    known_emails = [u["email"] for u in users]

    # Step 4: Check for face duplication
    result, matched_email = recognize(image_path, known_encodings, known_emails)
    if result != "Unknown" and matched_email is not None:
        print(f"❌ Face already registered as {matched_email}")
        return {"status": "error", "message": f"Face already registered as {matched_email}"}

    # Step 5: Encode the new face
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        print("❌ No face found in the image.")
        return {"status": "error", "message": "No face found in the image."}

    faceprint = encodings[0].astype(np.float64).tolist()

    # Step 6: Save faceprint to this user's record
    db.users.update_one(
        {"email": email},
        {"$set": {"faceprint": faceprint}}
    )

    print(f"✅ Face registered for {email}")
    return {"status": "success", "message": f"Face registered for {email}"}
