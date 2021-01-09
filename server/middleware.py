import asyncio
import functools

from loguru import logger
from aiohttp import web

from server.models.entities import User


@web.middleware
async def error_middleware(request: web.Request, handler):
    """
    Catch HTTP client errors
    :return: json response
    """
    try:
        return await handler(request)
    except web.HTTPException as err:
        if err.status_code != 302:
            logger.error(err.text)
            return web.json_response({"error": err.text})
    except asyncio.CancelledError as err:
        logger.error(str(err))
        raise
    except Exception as err:
        logger.error(str(err))
        return web.json_response({"error": str(err)})


def auth_required(f):
    """
    A decorator that allows users to control access to the game api
    """

    @functools.wraps(f)
    async def wrapped(self):
        async with self.request.app["db"].acquire() as conn:
            user = await User.is_authorized(conn)
            if user:
                raise web.HTTPFound("/auth/")
        return await (f(self))

    return wrapped
