from loguru import logger
from aiohttp import web

from server.models.entities import User


class Index(web.View):
    """
    Main view for auth api
    path: /auth/
    """

    async def get(self):
        logger.info(self.request)
        async with self.request.app["db"].acquire() as conn:
            try:
                user = await User.get_user(conn)
                if user["disabled"]:
                    return web.json_response({"error": "Auth Required!"})
                else:
                    return web.json_response({"success": f"Welcome {user['username']}"})
            except ValueError:
                return web.json_response({"error": "You need to register"})


class Login(web.View):
    """
    Provides simple authorization mechanism with store active user in the database
    path: /auth/login
    """

    async def post(self):
        logger.info(self.request)
        user_data = await self.request.post()

        async with self.request.app["db"].acquire() as conn:
            error = await User.validate_login_data(conn, user_data)
            if error:
                return web.json_response({"error": error})

            await User.remember(conn)
            raise web.HTTPFound("/auth/")


class Logout(web.View):
    """
    path: /auth/logout
    """

    async def get(self):
        logger.info(self.request)
        async with self.request.app["db"] as conn:
            await User.forget(conn)
            raise web.HTTPFound("/auth/")


class Signup(web.View):
    """
    Simple user registration using log/pass
    The password is stored as hash
    path: /auth/signup
    """

    async def post(self):
        logger.info(self.request)
        user_data = await self.request.post()
        async with self.request.app["db"].acquire() as conn:
            error = await User.validate_register_data(conn, user_data)
            if error:
                return web.json_response({"error": error})

            await User.create_user(conn, user_data)
            return web.json_response({"success": f"User {user_data['username']} is created!"})


class Root(web.View):
    async def get(self):
        logger.info(f"{self.request.path} redirect to /auth/")
        raise web.HTTPFound("/auth/")
