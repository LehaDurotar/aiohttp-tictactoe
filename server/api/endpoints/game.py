from random import choice

from loguru import logger
from aiohttp import web
from psycopg2 import IntegrityError
from aiohttp_security import authorized_userid

from server.models.entities import GameInstance

from .index import redirect


async def start_game(request):
    """
    Shows created games or create a new game into the game table
    :param request: GET or POST request
    :return: rest response as json
    """
    if request.method == "GET":
        async with request.app["db"].aquire() as conn:
            cursor = await conn.execute(GameInstance.select())
            records = await cursor.fetchall()
            games = str([(i[0], i[1]) for i in records])
            logger.info(games)
            return web.json_response({"games": games})

    if request.method == "POST":
        data = await request.post()
        game_name = data["name"]
        try:
            async with request.app["db"].acquire() as conn:
                await conn.execute(GameInstance.insert().values(name=game_name, status="NEW"))
        except (KeyError, TypeError, ValueError) as err:
            raise web.json_response({"error": {f"{err}": "You have not specified a game name"}})
        except IntegrityError:
            raise web.json_response({"error": {"integrity": f"A game called {game_name} already exists."}})

        return web.json_response({"success": f"New Game: {game_name} has been created"})


async def next_move(request):
    raise NotImplemented
