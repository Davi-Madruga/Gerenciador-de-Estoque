FROM python:3.12-slim
WORKDIR /srv/estoque
RUN apt-get update && apt-get install -y --no-install-recommends build-essential pkg-config default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY manage.py .
COPY app app
COPY projeto projeto
CMD ["sh", "-c", "python manage.py migrate && exec python manage.py runserver 0.0.0.0:8003 --noreload"]
