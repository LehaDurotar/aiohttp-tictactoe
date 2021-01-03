from loguru import logger
from sqlalchemy import MetaData, create_engine

from server.models import moves, users, gamestats, gameinstance
from server.settings import config

DB_CFG = config["postgres"]
DSN = f"postgresql://{DB_CFG['user']}:{DB_CFG['password']}@localhost:5432/{DB_CFG['database']}"


def create_tables(engine) -> None:
    meta = MetaData()
    meta.create_all(bind=engine, tables=[users, gameinstance, moves, gamestats])
    logger.info("Create DB tables")


def drop_tables(engine) -> None:
    meta = MetaData()
    meta.drop_all(bind=engine, tables=[users, gameinstance, moves, gamestats])
    logger.info("Drop DB tables")


def drop_and_rebuild(engine) -> None:
    drop_tables(engine)
    create_tables(engine)


def setup() -> None:
    # Sets up a users and test database
    engine = create_engine(DSN)
    drop_and_rebuild(engine)


if __name__ == "__main__":
    setup()
