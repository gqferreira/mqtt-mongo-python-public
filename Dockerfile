FROM python:3.13-slim
WORKDIR /app-telemetry

RUN mkdir app

COPY app/app.py ./app
COPY app/config.py ./app
COPY app/db.py ./app
COPY app/mqtt_client.py ./app
COPY app/swagger.yaml ./app
COPY app/env ./app/env
COPY app/services ./app/services
COPY app/static ./app/static
COPY app/routes ./app/routes
COPY tests ./tests
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["python", "-m", "app.app"]
