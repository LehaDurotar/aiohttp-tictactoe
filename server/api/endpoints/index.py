from loguru import logger
from aiohttp import web
from aiohttp_session import get_session, new_session

from server.models.entities import Users


class Index(web.View):
    """
    Main view
    """

    async def get(self):
        logger.info(self.request.path)
        session = await get_session(self.request)
        if "username" not in session:
            return web.json_response({"error": "Auth Required!"})
        else:
            user = session["username"]
            async with self.request.app["db"].acquire() as conn:
                # curr_user = await Users.get_user_by_name(conn, user)
                stats = ""
                return web.json_response({"success": {user: stats}})


class Login(web.View):
    """"""

    async def get(self):
        logger.info(self.request.path)
        session = await get_session(self.request)
        user = session["username"]
        if user:
            raise web.HTTPFound("/auth/")

    async def post(self):
        logger.info(self.request.path)
        session = await new_session(self.request)
        user_data = await self.request.post()

        async with self.request.app["db"].acquire() as conn:
            error = await Users.validate_login_data(conn, user_data)
            if error:
                return web.json_response({"error": error})
            else:
                session["username"] = user_data["username"]

            return web.HTTPFound("/auth/login")


class Logout(web.View):
    """"""

    async def get(self):
        logger.info(self.request.path)
        session = await get_session(self.request)
        session["username"] = None
        return web.json_response({"success": "logout"})


class Signup(web.View):
    """"""

    async def post(self):
        logger.info(self.request.path)
        # session = await get_session(self.request)
        user_data = await self.request.post()
        async with self.request.app["db"].acquire() as conn:
            error = await Users.validate_register_data(conn, user_data)
            if error:
                return web.json_response({"error": error})

            await Users.create_user(conn, user_data)
            # session["username"] = user_data["username"]
            return web.json_response({"success": f"User {user_data['username']} is created!"})
