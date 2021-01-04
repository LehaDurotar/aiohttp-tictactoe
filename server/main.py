import aioredis
from loguru import logger
from server.settings import config
from server.api.routes import setup_routes
from aiohttp.web import Application, run_app
from server.db.database import init_pg, close_pg
from aiohttp_session import setup as setup_session
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session.redis_storage import RedisStorage
from aiojobs.aiohttp import setup as setup_aiojobs

from server.db.auth import DBAuthorizationPolicy


async def setup_redis(app: Application):
    """
    Create session storage with redis
    """
    cfg = app["config"]["redis"]
    pool = await aioredis.create_redis_pool((cfg["REDIS_HOST"], cfg["REDIS_PORT"]))

    async def close_redis(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_redis)
    app["redis_pool"] = pool
    return pool


async def init_app() -> Application:
    """
    Create an instance of the server and run it
    """
    app = Application()
    app["config"] = config
    setup_routes(app)
    app.on_startup.append(init_pg)
    engine = await init_pg(app)
    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(engine))
    logger.debug(app["config"])
    app.on_cleanup.append(close_pg)
    setup_aiojobs(app)
    return app


def main() -> None:
    app = init_app()
    run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
