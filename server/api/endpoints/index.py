from loguru import logger
from aiohttp import web
from aiohttp_security import forget, remember, authorized_userid

from server.db.database import create_user, get_user_by_name, validate_login_data, validate_register_data


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)


async def index(request):
    """
    Main page
    :param request:
    :return: json info about user and his game session
    """
    user = await authorized_userid(request)
    if not user:
        return web.json_response({"error": "Auth Required!"})

    async with request.app["db_pool"].acquire() as conn:
        curr_user = await get_user_by_name(conn, user)
        prev_stats = None
        return web.json_response({"user": curr_user, "stats": prev_stats})


async def login(request):
    user = await authorized_userid(request)
    if user:
        raise redirect(request.app.router, "index")

    if request.method == "POST":
        user_data = await request.post()

        async with request.app["db_pool"].acquire() as conn:
            error = await validate_login_data(conn, user_data)
            if error:
                return web.json_response({"error": error})

            response = redirect(request.app.router, "index")

            user = await get_user_by_name(conn, user_data["username"])
            await remember(request, response, user["username"])

            raise response
    else:
        raise redirect(request.app.router, "index")


async def logout(request):
    response = redirect(request.app.router, "login")
    await forget(request, response)
    return response


async def register(request):
    user_data = await request.post()
    async with request.app["db_pool"].acquire() as conn:
        error = await validate_register_data(conn, user_data)
        if error:
            return web.json_response({"error": error})

        await create_user(conn, user_data)
        return web.json_response({"success": f"User {user_data['username']} is created!"})
