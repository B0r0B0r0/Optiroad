FROM python:3.10-slim

# Install SUMO + tools
RUN apt-get update && \
    apt-get install -y sumo sumo-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV SUMO_HOME=/usr/share/sumo
# Workdir
WORKDIR /app

# Copy your code
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python", "main.py"]
