# Separate build image
FROM python:3.10-slim-buster as builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir setuptools wheel \
 && rm -rf /var/lib/apt/lists/*

# Final image
FROM builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/logs

ADD . /app
EXPOSE 5000
ENTRYPOINT ["uvicorn","main:app","--host","0.0.0.0","--port","5000","--log-config","log_2.conf"]
