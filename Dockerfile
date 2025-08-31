FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libtag1-dev \
    libyaml-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies (prefer binary wheels to avoid build issues)
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p downloads music_library playlists

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app/main.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
