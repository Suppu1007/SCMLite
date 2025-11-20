FROM python:3.10-slim

WORKDIR /app

<<<<<<< HEAD:server/Dockerfile
<<<<<<< HEAD
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install python-multipart python-dotenv
=======
=======

>>>>>>> dev:app/Dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


COPY ../app/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt
>>>>>>> dev


COPY ../app /app/app


COPY socket_server.py /app/socket_server.py

EXPOSE 8000

<<<<<<< HEAD:server/Dockerfile
<<<<<<< HEAD
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
=======
# IMPORTANT: Correct ASGI import path
=======
>>>>>>> dev:app/Dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> dev
