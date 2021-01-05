from aiohttp import web

from .endpoints.game import Game, MakeMove, ShowPlayers, ShowGameBoard, AddPlayerToGame
from .endpoints.index import Index, Login, Register

register_api = web.Application()
game_api = web.Application()


def setup_routes(app: web.Application):
    app.router.add_view("/", Index, name="index")

    register_api.router.add_view("/", Register, name="register")
    register_api.router.add_view("/login", Login, name="login")

    game_api.router.add_view("/", Game, name="game")
    game_api.router.add_view("/{game_name}/player", AddPlayerToGame, name="add_player_to_game")
    game_api.router.add_view("/{game_name}/player/{player_name}/move", MakeMove, name="make_move")
    game_api.router.add_view("/{game_name}/board", ShowGameBoard, name="show_game_board")
    game_api.router.add_view("/players", ShowPlayers, name="show_players")

    app.add_subapp("/register/", register_api)
    app.add_subapp("/game/", game_api)

    register_api["db"] = app["db"]
    game_api["db"] = app["db"]
