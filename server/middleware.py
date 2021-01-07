import functools

from loguru import logger
from aiohttp import web

from server.models.entities import User


@web.middleware
async def error_middleware(request: web.Request, handler):
    """
    Catch uncaught exceptions
    """
    try:
        response = await handler(request)
        if response.status != 404:
            return response
        message = response.message
    except web.HTTPException as ex:
        if ex.status != 404:
            raise
        message = ex.body
    logger.error(message)
    return web.json_response({"error": message})


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
