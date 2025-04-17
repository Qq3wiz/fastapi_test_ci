FROM python:3.8-slim

WORKDIR /app

COPY ../requirements.dev.txt /app/requirements.dev.txt

RUN pip install -r requirements.dev.txt

COPY ../src/ /app/src/
COPY ../tests/ /app/tests/


CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]