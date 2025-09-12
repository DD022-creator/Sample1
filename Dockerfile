FROM tensorflow/tensorflow:2.13.0-gpu

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/input /data/output

ENTRYPOINT ["python", "main.py", "--input_dir", "/data/input", "--output_file", "/data/output/results.json"]