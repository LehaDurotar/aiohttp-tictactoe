from loguru import logger
from aiohttp.web import Application, run_app

from server.settings import config
from server.api.routes import setup_routes
from server.middleware import error_middleware
from server.db.database import close_pg, init_or_get_pg


async def init_app() -> Application:
    """
    Create an instance of the server and run it
    """
    app = Application(middlewares=[error_middleware])
    app["config"] = config

    engine = await init_or_get_pg(app)
    setup_routes(app, engine)
    logger.debug(app["config"])

    app.on_startup.append(init_or_get_pg)
    app.on_cleanup.append(close_pg)

    return app


def main() -> None:
    app = init_app()
    run_app(app)


if __name__ == "__main__":
    main()
