FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    default-jre \
    locales \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

ENV JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 🔥 QUAN TRỌNG
ENV PORT=8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]