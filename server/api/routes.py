from aiohttp import web

from .endpoints.auth import Root, Index, Login, Logout, Signup
from .endpoints.game import AddGame, GameList, MakeMove, ShowGameBoard, AddPlayerToGame

auth_api = web.Application()
game_api = web.Application()


def setup_routes(app: web.Application, engine):
    app.router.add_view("/", Root, name="root")

    auth_api.router.add_view("/", Index, name="index")

    auth_api.router.add_view("/signup", Signup, name="signup")
    auth_api.router.add_view("/login", Login, name="login")
    auth_api.router.add_view("/logout", Logout, name="logout")

    game_api.router.add_view("/", AddGame, name="add_game")
    game_api.router.add_view("/list", GameList, name="game_list")
    game_api.router.add_view("/{game_name}/add", AddPlayerToGame, name="add_player_to_game")
    game_api.router.add_view("/{game_name}/move", MakeMove, name="make_move")
    game_api.router.add_view("/{game_name}/board", ShowGameBoard, name="show_game_board")

    app.add_subapp("/auth/", auth_api)
    app.add_subapp("/game/", game_api)

    auth_api["db"] = engine
    game_api["db"] = engine
