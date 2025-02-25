FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for voice processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Try different installation methods for robustness
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt || \
    (pip install --no-cache-dir torch==2.0.1 torchaudio==2.0.2 --extra-index-url https://download.pytorch.org/whl/cpu && \
     pip install --no-cache-dir -r requirements.txt)

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 