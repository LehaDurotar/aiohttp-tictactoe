import datetime
from typing import Dict, List, Union

import aiopg.sa
from gino import Gino
from loguru import logger
from sqlalchemy import Table, Column, inspect

from server.settings import POSTGRES_URI

db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: Table = inspect(self.__class__)
        primary_key_columns: List[Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name]) for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=db.func.now(),
    )


async def init_pg(app):
    """
    :return: Connect to Postgres
    """
    if "db" in app:
        return app["db"]
    engine = await aiopg.sa.create_engine(dsn=POSTGRES_URI)
    logger.info(f"Setup DB Connection")
    app["db"] = engine
    return engine


async def validate_login_data(conn, data: Dict[str, str]) -> Union[str, None]:
    """
    Simple login data validation from POST request
    :param conn: DB pool
    :param data: login, pass
    :return: Specific error or None if check passed
    """
    username, password = data["username"], data["password"]

    if not username:
        return "username is required"
    if not password:
        return "password is required"

    # user = await get_user_by_name(conn, username)
    # if not user:
    #     return "invalid username"
    # if not check_password_hash(password, user["password_hash"]):
    #     return "invalid password"
    # else:
    #     return None


async def validate_register_data(conn, data: Dict[str, str]) -> Union[str, None]:
    """
    Simple register data validation from POST request
    :param conn: DB pool
    :param data: login, pass
    :return: Specific error or None if check passed
    """
    username, password = data["username"], data["password"]

    if not username:
        return "username is required"
    if not password:
        return "password is required"
    # user = await get_user_by_name(conn, username)
    # if user:
    #     return "This user already exists"
    # else:
    #     return None


async def close_pg(app) -> None:
    """
    Close DB connection
    """
    app["db"].close()
    await app["db"].wait_closed()
    logger.info("DB connection is closed")
