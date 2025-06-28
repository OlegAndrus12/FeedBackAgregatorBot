# Use official Python base image
FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-interaction --no-ansi --verbose

COPY . /app

RUN chmod +x compile-translation.sh

CMD ["poetry", "run", "python", "main.py"]
