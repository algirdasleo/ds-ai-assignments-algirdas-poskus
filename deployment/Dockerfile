FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ~/.local/bin/poetry config virtualenvs.create false

COPY ../capstone_project ../pyproject.toml ../poetry.lock ./

RUN ls -la
RUN poetry install --only=main

EXPOSE 8080
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENV PORT=8080

ENTRYPOINT ["poetry", "run", "python", "run.py"]