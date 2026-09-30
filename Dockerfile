FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/

COPY frontend/ /app/frontend/

EXPOSE 8000

ENTRYPOINT ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]

CMD ["--port", "8000"]