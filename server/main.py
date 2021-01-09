from loguru import logger
from aiohttp.web import Application, run_app

from server.settings import POSTGRES_URI
from server.api.routes import setup_routes
from server.middleware import error_middleware
from server.db.database import close_pg, init_or_get_pg


async def init_app(pg_url=None) -> Application:
    """
    Create an instance of the server and run it
    """
    # for gunicorn run
    if not pg_url:
        pg_url = POSTGRES_URI

    app = Application(middlewares=[error_middleware])
    app["config"] = pg_url

    engine = await init_or_get_pg(app, pg_url)
    setup_routes(app, engine)
    logger.debug(app["config"])

    app.on_cleanup.append(close_pg)

    return app


def main() -> None:
    """
    Local run
    """
    app = init_app(POSTGRES_URI)
    run_app(app)


if __name__ == "__main__":
    main()
