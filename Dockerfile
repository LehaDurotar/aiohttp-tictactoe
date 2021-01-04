FROM python:3.8
COPY pyproject.toml /

ENV PYTHONBUFFERED=1

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
# RUN poetry install --no-dev
WORKDIR /app

ADD . /app/
