import aioredis
from loguru import logger
from db.auth import DBAuthorizationPolicy
from settings import config
from api.routes import setup_routes
from aiohttp.web import Application, run_app
from db.database import close_pg, init_pg_pool
from aiohttp_session import setup as setup_session
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session.redis_storage import RedisStorage


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
    dp_pool = await init_pg_pool(app)
    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(dp_pool))
    logger.debug(app["config"])
    app.on_shutdown.append(close_pg)

    return app


def main() -> None:
    app = init_app()
    run_app(app)


if __name__ == "__main__":
    main()
