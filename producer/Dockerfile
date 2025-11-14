FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install kafka-python && \
    pip install python-dotenv

COPY producer.py /app/

CMD ["python", "producer.py"]
