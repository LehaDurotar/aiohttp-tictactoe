import functools

import aiohttp_session
from loguru import logger
from aiohttp import web


@web.middleware
async def error_middleware(request: web.Request, handler):
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
    @functools.wraps(f)
    async def wrapped(self, request):
        session = await aiohttp_session.get_session(request)
        if "username" not in session:
            raise web.HTTPUnauthorized()
        return await f(self, request)

    return wrapped
