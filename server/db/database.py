from typing import Dict, Union

import aiopg.sa
from loguru import logger

from server.models import users

from .security import check_password_hash, generate_password_hash


async def init_pg_pool(app):
    """
    :return: Connect to Postgres
    """
    cfg = app["config"]["postgres"]
    pool = await aiopg.create_pool(
        dsn=f"postgresql://{cfg['user']}:{cfg['password']}@localhost:5432/{cfg['database']}"
    )
    logger.info(f"Setup DB POOL")
    app["dp_pool"] = pool
    return pool


async def get_user_by_name(conn, username: str):
    result = await conn.fetchrow(users.select().where(users.c.username == username))
    return result


async def create_user(conn, user_data: dict) -> None:
    """
    Create new record in DB
    """
    username, password = user_data["username"], user_data["password"]
    hashed_pass = generate_password_hash(password)
    query = users.insert().values(username=username, password_hash=hashed_pass)
    await conn.execute(query)


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

    user = await get_user_by_name(conn, username)
    if not user:
        return "invalid username"
    if not check_password_hash(password, user["password_hash"]):
        return "invalid password"
    else:
        return None


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
    user = await get_user_by_name(conn, username)
    if user:
        return "This user already exists"
    else:
        return None


async def close_pg(app) -> None:
    """
    Close DB connection
    """
    app["db_pool"].close()
    await app["db_pool"].wait_closed()
    logger.info("DB connection is closed")
