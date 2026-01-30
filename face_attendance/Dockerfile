FROM ageitgey/face_recognition:latest

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy only requirements first (cache-friendly)
COPY requirements.txt .

# Upgrade pip only (no system builds)
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 10000

CMD ["python", "app.py"]
