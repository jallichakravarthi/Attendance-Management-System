FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV CMAKE_ARGS="-DDLIB_USE_CUDA=0 -DDLIB_USE_CUBLAS=0"
ENV DLIB_NO_GUI_SUPPORT=1
ENV MAKEFLAGS="-j1"

RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# 🔥 CRITICAL: prevent source builds
RUN pip install --no-cache-dir --only-binary=:all: dlib==19.24.1

RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["python", "app.py"]
