from aiohttp import web

from .endpoints.index import index, login, logout, register
from .endpoints.game import start_game, next_move


def setup_routes(app):
    app.router.add_get("/", index, name="index")
    app.router.add_get("/login", login, name="login")
    app.router.add_post("/login", login, name="login")
    app.router.add_get("/logout", logout, name="logout")
    app.router.add_post("/register", register, name="register")
