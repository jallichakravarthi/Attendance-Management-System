FROM python:3.10

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
