#FROM python:3.7-slim
FROM python:3.9.8-slim-bullseye

RUN groupadd -r cryptostacker && useradd --no-log-init -r -g cryptostacker cryptostacker

COPY --chown=cryptostacker:cryptostacker . /app

WORKDIR /app

RUN rm -f Dockerfile

RUN apt-get update \
    && apt-get upgrade -y \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && date >> /app/image.txt

EXPOSE 8000

USER cryptostacker

CMD ["gunicorn", "--enable-stdio-inheritance", "--certfile=/app/certs/cert.pem", "--keyfile=/app/certs/new.key", "-w", "12", "-b", "0.0.0.0:8000", "cryptostacker:app"]
