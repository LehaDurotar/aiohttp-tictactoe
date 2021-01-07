FROM python:3.8
COPY pyproject.toml /

ENV PYTHONBUFFERED=1

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

WORKDIR /app

ADD . /app/
