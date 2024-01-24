FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code

COPY ./api/pyproject.toml .
ARG with_test
RUN pip3 install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root $with_test
COPY ./api/ .
COPY .env ./src/.env
EXPOSE 8000
