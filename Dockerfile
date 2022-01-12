####################################################################
## Base stage
FROM python:3.8 AS base

WORKDIR /app
ENV PYTHONUNBUFFERED 1

# Copying essential files
COPY ./dev_challenge/. .
COPY ./requirements.txt requirements.txt
COPY ./entrypoint.sh entrypoint.sh

# Installing requirements
RUN pip install -r requirements.txt

####################################################################
## App stage
FROM base AS app

ENTRYPOINT ["./entrypoint.sh"]

####################################################################
## Test stage
FROM base AS test

CMD ["./manage.py", "test", "cnab"]
