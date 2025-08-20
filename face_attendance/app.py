from flask import Flask, render_template, request, jsonify, abort
from jwt import InvalidTokenError, ExpiredSignatureError
import jwt
import register
import recognize
import os
import dotenv

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
    email = request.form.get('email')
    token = request.form.get('token')
    if not email:
        return jsonify({"error": "Email is required"})
    return render_template('register.html', email=email, token=token)

@app.route('/submit-face', methods=['POST'])
def submit_face():
    email = request.form.get('email')
    token = request.form.get('token')
    image = request.files.get('image')
    secret_key = os.getenv("SECRET_KEY")

    # Validate token again (server-side enforcement)
    if not email or not token:
        return jsonify({"status": "error", "message": "Missing email or token"})

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        print("Payload email:", payload.get("email"))
        print("Form email:", email)
        if payload.get("email") != email:
            return jsonify({"status": "error", "message": "Invalid token for email"})
    except InvalidTokenError:
        return jsonify({"status": "error", "message": "Invalid token"})
    except ExpiredSignatureError:
        return jsonify({"status": "error", "message": "Token expired"})

    # Save image
    filepath = f"uploads/{image.filename}"
    image.save(filepath)

    result = register.register_face_to_db(filepath, email)
    if result["status"] == "error":
        return jsonify(result)

    print(f"✅ Registered Successfully with email {email}")
    return jsonify({"status": "success", "message": f"Face registered for {email}"})

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5050)


