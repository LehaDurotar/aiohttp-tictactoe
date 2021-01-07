from loguru import logger
from aiohttp.web import Application, run_app
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage

from server.settings import config
from server.api.routes import setup_routes
from server.middleware import error_middleware
from server.db.database import init_pg, close_pg, setup_redis


async def init_app() -> Application:
    """
    Create an instance of the server and run it
    """
    app = Application(middlewares=[error_middleware])
    app["config"] = config

    engine = await init_pg(app)
    redis_pool = await setup_redis(app)

    setup_session(app, RedisStorage(redis_pool))
    setup_routes(app)
    logger.debug(app["config"])

    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    return app


def main() -> None:
    app = init_app()
    run_app(app)


if __name__ == "__main__":
    main()
