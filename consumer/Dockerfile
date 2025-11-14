FROM python:3.10-slim

WORKDIR /app

# Copy dependency file first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the consumer code
COPY . .

# Run the Kafka Consumer
CMD ["python", "consumer/consumer.py"]
