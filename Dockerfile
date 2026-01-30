FROM python:3.10-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for dlib
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better Docker caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port Render expects
EXPOSE 10000

# Start your Flask app
CMD ["python", "app.py"]
