FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates wget gnupg curl \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libcups2 libdrm2 libxshmfence1 libxkbcommon0 \
    fonts-liberation \
    xvfb fluxbox x11vnc \
    novnc websockify \
    net-tools procps \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"
RUN which uv && which uvx && uv --version && uvx --version

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 --retries=5 -r requirements.txt

RUN python -m playwright install --with-deps chromium

COPY . .
RUN mkdir -p /app/reports

EXPOSE 6080

ENTRYPOINT ["/bin/bash", "-lc", "\
  set -eux; \
  Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset & \
  sleep 2; \
  fluxbox & \
  sleep 1; \
  x11vnc -display :99 -forever -shared -nopw -rfbport 5900 -listen 127.0.0.1 -logfile /tmp/x11vnc.log & \
  sleep 2; \
  netstat -tulpn | grep 5900 >/dev/null || (echo '❌ x11vnc not listening'; cat /tmp/x11vnc.log; exit 1); \
  websockify --web=/usr/share/novnc/ 6080 127.0.0.1:5900 & \
  echo '✅ LIVE VIEW: http://localhost:6080/vnc.html'; \
  echo \"ARGS: $@\"; \
  python main.py \"$@\"; \
  echo 'main.py finished/crashed, keeping noVNC alive...'; \
  tail -f /tmp/x11vnc.log \
", "--"]
CMD []


