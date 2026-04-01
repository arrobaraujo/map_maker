FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:1 \
    VNC_PORT=5901 \
    NOVNC_PORT=6080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    libxinerama1 \
    libxcursor1 \
    libxrandr2 \
    libxi6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 6080 5901

RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]