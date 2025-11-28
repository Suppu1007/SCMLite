FROM python:3.10-slim

WORKDIR /app

COPY consumer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY consumer/consumer.py /app/consumer.py

CMD ["python", "consumer.py"]
