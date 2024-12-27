FROM python:3.10.13

RUN python3.10 -m pip install --upgrade pip
RUN python3.10 -m pip install poetry

WORKDIR /app

COPY . /app

RUN poetry install --no-interaction

CMD ["./docker-entrypoint.sh"]
