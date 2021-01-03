FROM python:3.8
COPY pyproject.toml /

ENV PYTHONBUFFERED=1

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
# RUN poetry install --no-dev
WORKDIR /app

COPY ./server /app/server
COPY ./scripts/runserver.sh /app/scripts/runserver.sh

RUN useradd tic_tac_toe_dev
RUN chown -R tic_tac_toe_dev:tic_tac_toe_dev /app
RUN chmod +x /app/scripts/runserver.sh

USER tic_tac_toe_dev

CMD ["/app/scripts/create_db_container.sh"]
CMD ["/app/scripts/runserver.sh"]