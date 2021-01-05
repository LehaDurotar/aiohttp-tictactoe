from random import choice
from itertools import combinations

from loguru import logger
from aiohttp import web
from psycopg2 import IntegrityError
from aiohttp_security import authorized_userid

from server.models.entities import Moves, Users, Player, GameInstance, GamePlayerStats

from .index import redirect


async def game(request):
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


# /game/{game_name}/player
async def add_player_to_game(request):
    try:

        game_name = request.match_info["game_name"]

        # the GET request retrieves all players for the game_name
        if request.method == "GET":

            # select all the players in game_name
            s = GamePlayerStats.select().where(Users.c.name == game_name)
            async with request.app["db"].acquire() as conn:
                cursor = await conn.execute(s)
                records = cursor.fetchall()
                raise web.json_response({"info": "players in game are: "})

        # the POST request inserts a new player for the game_name
        elif request.method == "POST":

            data = await request.post()
            player_name = data["player_name"]

            async with request.app["db"].acquire() as conn:
                # get the number of players in the game already
                cursor = await conn.execute(
                    GamePlayerStats.select().where(GamePlayerStats.c.game_name == game_name)
                )
                get_players = await cursor.fetchone()
                num_players = cursor.rowcount

                # tic tac toe can only have 2 players
                if num_players >= 2:
                    raise web.json_response({"error": "this game already has 2 players"})

                # if no players exist, this player is assigned crosses
                if num_players == 0:
                    await conn.execute(
                        GamePlayerStats.insert().values(
                            move_type="X", game_name=game_name, player_name=player_name
                        )
                    )
                    move_type = "crosses"

                    # this player will start the game so make it
                    # their turn
                    await conn.execute(
                        GameInstance.update()
                        .where(GameInstance.c.name == game_name)
                        .values(next_turn=player_name)
                    )
                # if we're here num_players must be 1
                else:
                    # we cannot add the same player to the same game
                    current_player = get_players["player_name"]

                    if player_name == current_player:
                        raise web.json_response({"error": "the game must have two different players"})

                    else:
                        await conn.execute(
                            GamePlayerStats.insert().values(
                                move_type="O", game_name=game_name, player_name=player_name
                            )
                        )

                        move_type = "noughts"

                        # switch the game to IN PROGRESS so players
                        # can start making moves.
                        await conn.execute(
                            GameInstance.update()
                            .where(GameInstance.c.name == game_name)
                            .values(status="IN PROGRESS")
                        )

                return web.json_response(
                    {
                        "success": {
                            "new player": f"New player: {player_name} has been added to game: {game_name} and is using {move_type}"
                        }
                    }
                )

    except (KeyError, TypeError, ValueError) as e:
        logger.error(e)
        raise web.json_response({"error": {f"{e}": "You have not specified a game or player name"}})

    except IntegrityError as e:
        logger.error(e)
        raise web.json_response(
            {"error": {f"{e}": "The game does not exist or the player POST data is incorrect"}}
        )

    return web.json_response({"error": "Wrong request type"})


# /game/{game_name}/player/{player_name}/move
async def make_move(request):
    """
    Algorithm for finding winner assigns numbers to each square
    so that all rows diagonals etc add to 15, if same X or O in any of
    these given rows or diagonals then we have a winner
    User still enters numbers 1 to 9 for squares left to right,
    top to bottom though so it isn't confusing for them
    An index in this list is the user square, the number stored
    at that index is the square used for calculating the winner
    """

    square_list = [4, 3, 8, 9, 5, 1, 2, 7, 6]
    game_name = request.match_info["game_name"]
    player_name = request.match_info["player_name"]

    data = await request.post()

    try:
        move_square = data["square"]

    except (KeyError, TypeError, ValueError) as e:
        logger.error(e)
        raise web.json_response({"error": {f"{e}": "You have not requested a square correctly"}})

    # next two if statements make sure square value is valid
    if not isinstance(move_square, int):
        raise web.json_response({"error": "square must be a number"})

    move_square = int(move_square)

    if move_square < 1 or move_square > 9:
        raise web.json_response({"error": "square must be between 1 and 9"})

    async with request.app["db"].acquire() as conn:
        # game must be IN PROGRESS
        # this is initially set in the add_player_to_game view
        cursor = await conn.execute(GameInstance.select().where(GameInstance.c.name == game_name))

        result = await cursor.fetchone()
        game_status = result["status"]
        next_turn = result["next_turn"]

        if game_status != "IN PROGRESS":
            raise web.json_response({"error": "To make a move the game must be in progress"})

        # the player must be playing in this game
        cursor = await conn.execute(GamePlayerStats.select().where(GamePlayerStats.c.game_name == game_name))
        current_game = await cursor.fetchall()
        move_type = [i[1] for i in current_game if i[3] == player_name][0]
        participants = [i[3] for i in current_game]

        if not (player_name in participants):
            raise web.json_response({"error": {f"{player_name}": "Player is not playing this game"}})

        # check if it's this players turn
        if next_turn != player_name:
            raise web.json_response({"error": "It is not this players turn"})

        # cant move to same square twice
        cursor = await conn.execute(Moves.select().where(Moves.c.game_name == game_name))

        all_moves = await cursor.fetchall()
        all_squares = [i[1] for i in all_moves]

        if move_square in all_squares:
            raise web.json_response({"error": f"Square {move_square} has already been used"})

        # insert the new move
        await conn.execute(
            Moves.insert().values(
                square=move_square, move_type=move_type, game_name=game_name, player_name=player_name
            )
        )

        # determine if there is a winner or all squares are filled
        # this gets all moves by the current player
        player_squares_list = [i[1] for i in all_moves if i[4] == player_name]
        # add current move to the list
        player_squares_list.append(move_square)
        squares_for_sum = [square_list[i - 1] for i in player_squares_list]
        # check if a combination of squares add to 15
        winner = subset_sum(squares_for_sum, 15)

        # update game status to FINISHED
        if winner:
            await conn.execute(
                GameInstance.update().where(GameInstance.c.name == game_name).values(status="FINISHED")
            )
            return web.json_response({"success": {f"{player_name}": "Congratulations You won the game."}})

        # check if all squares have been filled
        # update status to FINISHED - NO WINNER
        if len(all_moves) + 1 == 9:
            await conn.execute(
                GameInstance.update()
                .where(GameInstance.c.name == game_name)
                .values(status="FINISHED - NO WINNER")
            )
            return web.json_response({"success": "Game Over: No Winner, all squares filled"})

        # if no winner and game is still going update whose turn it is
        next_player = [i for i in participants if i != player_name][0]

        await conn.execute(
            GameInstance.update().where(GameInstance.c.name == game_name).values(next_turn=next_player)
        )

    return web.json_response({f"{player_name}": f"moved an {move_type} to square {move_square}"})


# /game/{game_name}/show
async def show_game_board(request):
    game_name = request.match_info["game_name"]

    async with request.app["db"].acquire() as conn:
        cursor = await conn.execute(Moves.select().where(Moves.c.game_name == game_name))
        all_moves = await cursor.fetchall()

        moves_dict = {i[1]: i[2] for i in all_moves}
        moves_str = "\n"
        for i in range(1, 10):
            if i in moves_dict:
                moves_str += moves_dict[i] + " "
            else:
                moves_str += "  "
            if i % 3 == 0:
                moves_str += "\n"

    return web.json_response({"success": moves_str})


async def show_or_insert_players(request):
    # show all players
    if request.method == "GET":
        async with request.app["db"].acquire() as conn:
            s = Player.select()
            cursor = await conn.execute(s)
            records = await cursor.fetchall()
            players = str([i[0] for i in records])
            return web.Response(text="players are: " + players)

    elif request.method == "POST":
        data = await request.post()

        try:
            player_name = data["player_name"]

        except (KeyError, TypeError, ValueError) as e:
            logger.error(e)
            raise web.json_response({"error": {f"{e}": "You have not requested a player correctly"}})

        # check if player has been added to player table
        # if not we'll add it
        async with request.app["db"].acquire() as conn:
            s = Player.select().where(Player.c.name == player_name)
            cursor = await conn.execute(s)
            row_count = cursor.rowcount

            # add player to player table if it doesn't exist
            if row_count == 0:
                await conn.execute(Player.insert().values(name=player_name))
            else:
                raise web.json_response({"error": f"A player with name {player_name} has already been added"})

            return web.json_response({"success": f"Player: {player_name} was successfully added."})

    return web.json_response({})


def subset_sum(lst, target):
    return len(lst) > 2 and any(sum(x) == target for x in combinations(lst, 3))
