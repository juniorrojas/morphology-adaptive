FROM python:3.11

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    chromium && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

RUN pip install uv

RUN uv pip install --system torch==2.7.0

RUN mkdir /morphology-adaptive
COPY ./scripts /morphology-adaptive/scripts

RUN python /morphology-adaptive/scripts/install_algovivo.py --system --repo-dirname /morphology-adaptive/algovivo.repo

ENV PYTHONPATH=/morphology-adaptive
ENV ALGOVIVO_NATIVE_LIB_FILENAME=/morphology-adaptive/algovivo.repo/build/native/algovivo.so

COPY ./data /morphology-adaptive/data
COPY ./attn /morphology-adaptive/attn

COPY ./attn /morphology_adaptive/attn

RUN npm ci --prefix /morphology-adaptive/algovivo.repo