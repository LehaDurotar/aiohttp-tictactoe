from loguru import logger
from aiohttp import web
from aiohttp_security import forget, remember, authorized_userid

from server.models.entities import Users


def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)


class Index(web.View):
    """
    Main view
    """

    async def get(self):
        logger.info(self.request.path)
        user = await authorized_userid(self.request)
        if not user:
            return web.json_response({"error": "Auth Required!"})
        async with self.request.app["db"].acquire() as conn:
            curr_user = await Users.get_user_by_name(conn, user)
            prev_stats = None
            return web.json_response({"user": curr_user, "stats": prev_stats})


class Login(web.View):
    """"""

    async def get(self):
        logger.info(self.request.path)
        user = await authorized_userid(self.request)
        if user:
            raise redirect(self.request.app.router, "index")

    async def post(self):
        logger.info(self.request.path)
        user_data = await self.request.post()

        async with self.request.app["db"].acquire() as conn:
            error = await Users.validate_login_data(conn, user_data)
            if error:
                return web.json_response({"error": error})

            response = redirect(self.request.app.router, "index")

            user = await Users.get_user_by_name(conn, user_data["username"])
            await remember(self.request, response, user["username"])

            raise response


class Logout(web.View):
    """"""

    async def get(self):
        logger.info(self.request.path)
        response = redirect(self.request.app.router, "login")
        await forget(self.request, response)
        return response


class Register(web.View):
    """"""

    async def post(self):
        logger.info(self.request.path)
        user_data = await self.request.post()
        async with self.request.app["db"].acquire() as conn:
            error = await Users.validate_register_data(conn, user_data)
            if error:
                return web.json_response({"error": error})

            await Users.create_user(conn, user_data)
            response = redirect(self.request.app.router, "index")
            await remember(self.request, response, user_data["username"])
            return web.json_response({"success": f"User {user_data['username']} is created!"})
