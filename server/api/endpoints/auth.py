from loguru import logger
from aiohttp import web
from pydantic import ValidationError

from server.models.entities import User
from server.schemas.validators.user import UserLogin, UserSignup


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

        try:
            UserLogin(username=user_data.get("username"), password=user_data.get("password"))
        except ValidationError as err:
            return web.Response(body=err.json())

        async with self.request.app["db"].acquire() as conn:
            await User.remember(conn, user_data["password"])
            # raise web.HTTPFound("/auth/")
            return web.json_response({"success": "You are logged in!"})


class Logout(web.View):
    """
    path: /auth/logout
    """

    async def get(self):
        logger.info(self.request)
        async with self.request.app["db"].acquire() as conn:
            await User.forget(conn)
            # raise web.HTTPFound("/auth/")
            return web.json_response({"success": "You have logged out!"})


class Signup(web.View):
    """
    Simple user registration using log/pass
    The password is stored as hash
    path: /auth/signup
    """

    async def post(self):
        logger.info(self.request)
        user_data = await self.request.post()

        try:
            UserSignup(
                username=user_data.get("username"),
                password=user_data.get("password"),
                confirm=user_data.get("confirm"),
            )
        except ValidationError as err:
            return web.Response(body=err.json())

        async with self.request.app["db"].acquire() as conn:
            await User.create_user(conn, user_data)
            return web.json_response({"success": f"User {user_data['username']} is created!"})


class Root(web.View):
    async def get(self):
        logger.info(f"{self.request.path} redirect to /auth/")
        raise web.HTTPFound("/auth/")
