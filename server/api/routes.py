from aiohttp import web

from .endpoints.game import next_move, start_game
from .endpoints.index import index, login, logout, register


def setup_routes(app):
    app.router.add_get("/", index, name="index")
    app.router.add_get("/login", login, name="login")
    app.router.add_post("/login", login, name="login")
    app.router.add_get("/logout", logout, name="logout")
    app.router.add_post("/register", register, name="register")
    app.router.add_get("/start_game", start_game, name="start_game")
    app.router.add_post("/start_game", start_game, name="start_game")
