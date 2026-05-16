FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry && poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

COPY . .

RUN mkdir -p /data

ENV DB_PATH=/data/app.db

EXPOSE 8000

CMD [".venv/bin/fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
