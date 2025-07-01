FROM python:3.13.5-alpine

RUN pip install --no-cache-dir poetry==2.1.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

COPY src ./src

CMD ["poetry", "run", "fastapi", "run", "src/main.py"]