FROM python:3.8-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libgdal-dev \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyInstaller
RUN pip install --no-cache-dir pyinstaller

# Copy application files
COPY . .

# Run the build script
CMD ["python", "build.py"] 