# Usa una imagen oficial de Python 3
FROM python:3.11

# Actualiza pip a la última versión
RUN python -m pip install --upgrade pip

# Copia el contenido del proyecto al contenedor
COPY . /usr/src/app

# Establecer directorio de trabajo
WORKDIR /usr/src/app

# Instala dependencias del sistema necesarias para Kivy (incluyendo gstreamer)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-setuptools \
    python3-dev \
    build-essential \
    libgl1-mesa-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-alsa \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-x && \
    rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ejecuta la aplicación Python
CMD ["python", "Geolocalizacion.py"]