from random import choice
from itertools import combinations

from loguru import logger
from aiohttp import web
from psycopg2 import IntegrityError

from server.middleware import auth_required
from server.models.entities import Moves, Players, GameInstance, GamePlayerStats


class GameList(web.View):
    """
    Shows created games
    path: /game/list
    """

    @auth_required
    async def get(self):
        logger.info(self.request.path)
        async with self.request.app["db"].acquire() as conn:
            cursor = await conn.execute(GameInstance.query)
            records = await cursor.fetchall()
            if records is None:
                return web.json_response({"error": "You have not created any game session"})
            games = str([(i[0], i[1]) for i in records])
            logger.info(games)
            return web.json_response({"games": games})


class AddGame(web.View):
    """
    Create a new game session
    """

    @auth_required
    async def get(self):
        logger.info(self.request)
        return web.json_response({"info": "Create game with POST request"})

    @auth_required
    async def post(self):
        logger.info(self.request)
        data = await self.request.post()
        game_name = data["name"]
        try:
            async with self.request.app["db"].acquire() as conn:
                await conn.execute(GameInstance.insert().values(name=game_name, status="NEW"))
        except (KeyError, TypeError, ValueError) as err:
            return web.json_response({"error": {f"{err}": "You have not specified a game name"}})
        except IntegrityError:
            return web.json_response({"error": {"integrity": f"A game called {game_name} already exists."}})

        return web.json_response({"success": f"New Game: {game_name} has been created"})


class AddPlayerToGame(web.View):
    """
    The GET request retrieves all players for the game_name
    The POST request inserts a new player for the game_name
    path: /game/{game_name}/add
    """

    @auth_required
    async def post(self):
        logger.info(self.request)
        game_name = self.request.match_info["game_name"]
        data = await self.request.post()
        player_name = data["username"]

        try:
            async with self.request.app["db"].acquire() as conn:
                # get the number of players in the game already
                cursor = await conn.execute(
                    GamePlayerStats.query.where(GamePlayerStats.game_name == game_name)
                )
                num_players = cursor.rowcount

                if player_name == "computer":
                    raise web.json_response({"error": "the game must have two different players"})

                # tic tac toe can only have 2 players
                if num_players > 2:
                    return web.json_response({"error": "This game already has 2 players"})

                await conn.execute(Players.insert().values(name=player_name))

                # if no players exist, this player is assigned crosses
                query = GamePlayerStats.insert().values(
                    move_type="X", game_name=game_name, player_name=player_name
                )
                await conn.execute(query)

                # this player will start the game so make it
                await conn.execute(
                    GameInstance.update.where(GameInstance.name == game_name).values(next_turn=player_name)
                )

                await conn.execute(Players.insert().values(name="computer"))

                # mark the second player as computer
                await conn.execute(Players.update.where(Players.name == "computer").values(is_computer=True))
                await conn.execute(
                    GamePlayerStats.insert().values(
                        move_type="O", game_name=game_name, player_name="computer"
                    )
                )
                # switch the game to IN PROGRESS so players
                # can start making moves.
                await conn.execute(
                    GameInstance.update.where(GameInstance.name == game_name).values(status="IN PROGRESS")
                )

                return web.json_response(
                    {
                        "success": [
                            {
                                "player": f"{player_name} has been added to game: {game_name} and is using crosses"
                            },
                            {
                                "computer": f"Computer has benn added to game: {game_name} and is using noughts"
                            },
                        ]
                    }
                )

        except (KeyError, TypeError, ValueError) as e:
            logger.error(e)
            return web.json_response({"error": {f"{e}": "You have not specified a game or player name"}})

        except IntegrityError as e:
            logger.error(e)
            return web.json_response(
                {"error": {f"{e}": "The game does not exist or the player POST data is incorrect"}}
            )


class MakeMove(web.View):
    """
    Algorithm for finding winner assigns numbers to each square
    so that all rows diagonals etc add to 15, if same X or O in any of
    these given rows or diagonals then we have a winner
    User still enters numbers 1 to 9 for squares left to right,
    top to bottom though so it isn't confusing for them
    An index in this list is the user square, the number stored
    at that index is the square used for calculating the winner
    path: /game/{game_name}/move
    """

    @auth_required
    async def post(self):
        logger.info(self.request)
        square_list = [4, 3, 8, 9, 5, 1, 2, 7, 6]
        game_name = self.request.match_info["game_name"]
        data = await self.request.post()

        try:
            move_square = int(data["square"])

        except (KeyError, TypeError, ValueError) as e:
            logger.exception(e)
            return web.json_response({"error": {f"{e}": "You have not requested a square correctly"}})

        if move_square < 1 or move_square > 9:
            return web.json_response({"error": "square must be between 1 and 9"})

        async with self.request.app["db"].acquire() as conn:
            # game must be IN PROGRESS
            # this is initially set in the add_player_to_game view

            cursor = await conn.execute(
                GamePlayerStats.query.where(
                    GamePlayerStats.game_name == game_name and GamePlayerStats.player_name != "computer"
                )
            )
            player_record = await cursor.fetchone()
            player_name = player_record["player_name"]

            cursor = await conn.execute(GameInstance.query.where(GameInstance.name == game_name))

            result = await cursor.fetchone()
            game_status = result["status"]
            next_turn = result["next_turn"]

            if game_status != "IN PROGRESS":
                return web.json_response({"error": "To make a move the game must be in progress"})

            # the player must be playing in this game
            cursor = await conn.execute(GamePlayerStats.query.where(GamePlayerStats.game_name == game_name))
            current_game = await cursor.fetchall()
            move_type = [i[1] for i in current_game if i[3] == player_name][0]
            participants = [i[3] for i in current_game]

            if not (player_name in participants):
                return web.json_response({"error": {f"{player_name}": "Player is not playing this game"}})

            # check if it's this players turn
            if next_turn != player_name:
                return web.json_response({"error": "It is not this players turn"})

            # cant move to same square twice
            cursor = await conn.execute(Moves.query.where(Moves.game_name == game_name))

            all_moves = await cursor.fetchall()
            all_squares = [i[1] for i in all_moves]

            if move_square in all_squares:
                return web.json_response({"error": f"Square {move_square} has already been used"})

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
                    GameInstance.update.where(GameInstance.name == game_name).values(status="FINISHED")
                )
                return web.json_response({"success": {f"{player_name}": "Congratulations You won the game."}})

            # check if all squares have been filled
            # update status to FINISHED - NO WINNER
            if len(all_moves) + 1 == 9:
                await conn.execute(
                    GameInstance.update.where(GameInstance.name == game_name).values(
                        status="FINISHED - NO WINNER"
                    )
                )
                return web.json_response({"success": "Game Over: No Winner, all squares filled"})

            # if no winner and game is still going update whose turn it is
            next_player = [i for i in participants if i != player_name][0]

            await conn.execute(
                GameInstance.update.where(GameInstance.name == game_name).values(next_turn=next_player)
            )
            # computer section
            # get all free squares
            poss_squares = set(square_list).difference(set(all_squares))

            # choose a random free square for the computer move
            if len(poss_squares) == 0:
                computer_move_square = choice(square_list)
            else:
                computer_move_square = choice(list(poss_squares))

            # insert computer move in the moves table and switch player
            await conn.execute(
                Moves.insert().values(
                    square=computer_move_square,
                    move_type="O",
                    game_name=game_name,
                    player_name=next_player,
                )
            )
            await conn.execute(
                GameInstance.update.where(GameInstance.name == game_name).values(next_turn=player_name)
            )

        return web.json_response(
            {
                f"success": [
                    {player_name: f"Moved an {move_type} to square {move_square}"},
                    {next_player: f"Moved an O to square {computer_move_square}"},
                ]
            }
        )


class ShowGameBoard(web.View):
    """
    Show all moves on game field
    path: /game/{game_name}/board
    """

    @auth_required
    async def get(self):
        logger.info(self.request)
        game_name = self.request.match_info["game_name"]

        async with self.request.app["db"].acquire() as conn:
            cursor = await conn.execute(Moves.query.where(Moves.game_name == game_name))
            all_moves = await cursor.fetchall()

            moves_dict = {i[1]: i[2] for i in all_moves}

        return web.json_response({"success": moves_dict})


def subset_sum(sub: int, target: int):
    return len(sub) > 2 and any(sum(x) == target for x in combinations(sub, 3))
