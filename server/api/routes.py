from aiohttp import web

from .endpoints.game import Game, MakeMove, ShowPlayers, ShowGameBoard, AddPlayerToGame
from .endpoints.index import Root, Index, Login, Logout, Signup

auth_api = web.Application()
game_api = web.Application()


def setup_routes(app: web.Application, engine):
    app.router.add_view("/", Root, name="root")

    auth_api.router.add_view("/", Index, name="index")

    auth_api.router.add_view("/signup", Signup, name="signup")
    auth_api.router.add_view("/login", Login, name="login")
    auth_api.router.add_view("/logout", Logout, name="logout")

    game_api.router.add_view("/", Game, name="game")
    game_api.router.add_view("/{game_name}/player", AddPlayerToGame, name="add_player_to_game")
    game_api.router.add_view("/{game_name}/player/{player_name}/move", MakeMove, name="make_move")
    game_api.router.add_view("/{game_name}/board", ShowGameBoard, name="show_game_board")
    game_api.router.add_view("/players", ShowPlayers, name="show_players")

    app.add_subapp("/auth/", auth_api)
    app.add_subapp("/game/", game_api)

    auth_api["db"] = engine
    game_api["db"] = engine
