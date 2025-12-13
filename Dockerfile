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

ARG MORPHOLOGY_ADAPTIVE_DIRNAME=/morphology-adaptive
ARG ALGOVIVO_REPO_DIRNAME=${MORPHOLOGY_ADAPTIVE_DIRNAME}/algovivo.repo
ARG ALGOVIVO_SRC_REF=65e190859cd855f38942e71f4d841306c55de2c9
ARG ALGOVIVO_BUILD_REF=83ed37c28874490cb9434c35c5d7c3494befd797

RUN mkdir ${MORPHOLOGY_ADAPTIVE_DIRNAME}
COPY ./scripts ${MORPHOLOGY_ADAPTIVE_DIRNAME}/scripts

RUN python ${MORPHOLOGY_ADAPTIVE_DIRNAME}/scripts/install_algovivo.py \
    --system \
    --src-ref ${ALGOVIVO_SRC_REF} \
    --build-ref ${ALGOVIVO_BUILD_REF} \
    --repo-dirname ${ALGOVIVO_REPO_DIRNAME}

ENV PYTHONPATH=${MORPHOLOGY_ADAPTIVE_DIRNAME}
ENV ALGOVIVO_NATIVE_LIB_FILENAME=${ALGOVIVO_REPO_DIRNAME}/build/native/algovivo.so

COPY ./data ${MORPHOLOGY_ADAPTIVE_DIRNAME}/data
COPY ./attn ${MORPHOLOGY_ADAPTIVE_DIRNAME}/attn

COPY ./attn /morphology_adaptive/attn

RUN npm ci --prefix ${ALGOVIVO_REPO_DIRNAME}