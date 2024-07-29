# Usa un'immagine base ufficiale di Python
FROM python:3.9-slim

# Imposta il working directory
WORKDIR /app

# Installa le dipendenze di sistema richieste per OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    yasm \
    pkg-config \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavformat-dev \
    libpq-dev \
    libxine2-dev \
    libglew-dev \
    libtiff5-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libjasper-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libpostproc-dev \
    libswscale-dev \
    libeigen3-dev \
    libtbb-dev \
    libgtk2.0-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    python3-py \
    python3-pytest \
    libdc1394-22-dev \
    libxine2-dev \
    libv4l-dev \
    v4l-utils \
    qv4l2 \
    v4l2ucp \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libavresample-dev \
    libvorbis-dev \
    libxvidcore-dev \
    libx264-dev \
    x264 \
    v4l-utils \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Installa OpenCV usando pip
RUN pip install opencv-python-headless

# Copia il tuo codice nell'immagine Docker
COPY . /app

# Esegui lo script principale
CMD ["python", "main.py"]
