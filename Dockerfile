FROM python:3.11-slim

# install system dependencies (LibreOffice, ghostscript, poppler, qpdf)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    python3-uno \
    fonts-dejavu \
    ghostscript \
    poppler-utils \
    qpdf \
    build-essential \
    libmagic1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# working dir
WORKDIR /app

# copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY app ./app

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
