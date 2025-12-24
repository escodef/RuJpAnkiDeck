FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libsndfile1 \
    libsndfile1-dev \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1

WORKDIR /home/app

COPY ./data/freq_list.csv ./data/freq_list.csv

COPY tts/requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

RUN pip install -r requirements.txt

RUN python -m unidic download

COPY tts/main.py .
COPY shared/csv/ ./shared/csv

CMD ["python", "main.py"]
