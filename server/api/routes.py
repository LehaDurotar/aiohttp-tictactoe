from aiohttp import web

from .endpoints.game import game, make_move, show_game_board, add_player_to_game, show_or_insert_players
from .endpoints.index import index, login, logout, register


def setup_routes(app):
    app.router.add_get("/", index, name="index")
    app.router.add_post("/register", register, name="register")
    app.router.add_get("/game", game, name="start_game")
    app.router.add_post("/game", game, name="start_game")
    app.router.add_view("/game/{game_name}/player", add_player_to_game, name="add_player_to_game")
    app.router.add_post("/game/{game_name}/player/{player_name}/move", make_move, name="make_move")
    app.router.add_get("/game/{game_name}/board", show_game_board, name="show_game_board")
    app.router.add_view("/player", show_or_insert_players, name="show_or_insert_players")
