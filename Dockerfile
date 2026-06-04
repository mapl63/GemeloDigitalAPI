FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000
EXPOSE 8765

CMD sh -c "python -m websocket_servidor.server & uvicorn api:app --host 0.0.0.0 --port 10000"