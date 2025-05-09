FROM nvidia/cuda:12.6.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

RUN apt update && \
    apt -y upgrade && \
    apt install -y --no-install-recommends \
        software-properties-common \
        build-essential \
        python3-pip \
        python3-tk \
        python3-dev \
        git \
        bash \
        ffmpeg \
        libsm6 \
        libgl1 \
        libxrender1 \
        libxext6 \
        wget \
        curl \
        zip \
        unzip \
        libtcmalloc-minimal4 \
        ca-certificates && \
    update-ca-certificates && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /asr_service

COPY requirements.txt /asr_service/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121

RUN mkdir -p /asr_service/models_cache

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011"]