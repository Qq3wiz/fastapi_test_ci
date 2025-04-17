FROM python:3.8-slim

WORKDIR /app

COPY ../requirements.test.txt /app/requirements.test.txt

RUN pip install --no-cache-dir -r requirements.test.txt

COPY ../src/ /app/src/
COPY ../tests/ /app/tests/


CMD ["pytest", "tests/", "-v"]