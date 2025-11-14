FROM python:3.10-slim

WORKDIR /app

# Copy only what's needed
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the Kafka Producer
CMD ["python", "producer/producer.py"]
