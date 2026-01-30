from flask import Flask, render_template, request, jsonify, abort
import jwt
import register
import recognize
from mark_absentees import mark_absentees_if_window_closed
import os
import dotenv
from mongodb import get_db

dotenv.load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, This is is a Python flask server for face recognition microservice"

@app.route("/timings", methods=['GET'])
def attendance_timings():
    return jsonify({"start":os.getenv("START_TIME"),"end":os.getenv("END_TIME")})

@app.route('/register', methods=['POST'])
def register_ui():
    regNo = request.form.get('regNo')
    token = request.form.get('token')

    if not regNo:
        return jsonify({"error": "Registration Number is required"})

    regNo = regNo.upper().strip()
    print(f"Received registration request for regNo: {regNo}")

    return render_template('register.html', regNo=regNo, token=token)

@app.route('/submit-face', methods=['POST'])
def submit_face():
    regNo = request.form.get('regNo').strip().upper()
    token = request.form.get('token')
    image = request.files.get('image')
    secret_key = os.getenv("SECRET_KEY")

    if not regNo or not token or not image:
        return jsonify({"status": "error", "message": "Missing regNo, token, or image"})

    regNo = regNo.upper().strip()

    print(f"Submitting face for regNo: {regNo}")

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if payload.get("regNo") != regNo:
            return jsonify({"status": "error", "message": "Invalid token for regNo"})
    except ExpiredSignatureError:
        return jsonify({"status": "error", "message": "Token expired"})
    except InvalidTokenError:
        return jsonify({"status": "error", "message": "Invalid token"})

    filepath = f"uploads/{image.filename}"
    image.save(filepath)

    result = register.register_face_to_db(filepath, regNo)
    return jsonify(result)

@app.route('/recognize')
def recognize_ui():
    allowed_ips = ['127.0.0.1', '192.168.135.39']
    if request.remote_addr not in allowed_ips:
        print("aborting request from ",request.remote_addr)
        abort(403)  # Forbidden
    return render_template("recognize.html")

@app.route("/scan-face", methods=["POST"])
def scan_face():
    image = request.files["image"]
    filepath = "uploads/temp.jpg"
    image.save(filepath)

    result = recognize.recognize_and_mark_attendance(filepath)
    return jsonify({"result": result})

@app.route("/attendance/close-day", methods=["POST"])
def close_attendance():
    result = mark_absentees_if_window_closed()
    return jsonify(result)   # ✅ wrap dict in jsonify


def ensure_indexes():
    db = get_db()
    db.attendance.create_index(
        [("regNo", 1), ("date", 1)],
        unique=True
    )

if __name__ == "__main__":
    ensure_indexes()
    app.run(debug=True, host='0.0.0.0', port=5050)


