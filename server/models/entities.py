from typing import Dict, Union

from server.db.database import BaseModel, db
from server.db.security import check_password_hash, generate_password_hash


class User(BaseModel):
    """
    Base user model
    Authorized user can create game sessions
    """

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False, unique=True)
    disabled = db.Column(db.Boolean, nullable=False, default=True)

    @classmethod
    async def get_user(cls, conn):
        query = await conn.execute(User.query)
        user = await query.fetchone()
        return user

    @classmethod
    async def is_authorized(cls, conn) -> bool:
        user = await cls.get_user(conn)
        if user["disabled"]:
            return True
        return False

    @classmethod
    async def remember(cls, conn) -> None:
        user = await cls.get_user(conn)
        query = User.update.values(username=user["username"], disabled=False)
        await conn.execute(query)

    @classmethod
    async def forget(cls, conn) -> None:
        user = await cls.get_user(conn)
        query = User.update.values(username=user["username"], disabled=True)
        await conn.execute(query)

    @staticmethod
    async def create_user(conn, user_data: dict) -> None:
        username, password = user_data["username"], user_data["password"]
        hashed_pass = generate_password_hash(password)
        query = User.insert().values(username=username, password_hash=hashed_pass)
        await conn.execute(query)

    @classmethod
    async def validate_login_data(cls, conn, data: Dict[str, str]) -> Union[str, None]:
        """
        Simple login data validation from POST request
        :param conn: DB pool
        :param data: login, pass
        :return: Specific error or None if check passed
        """
        username, password = data["username"], data["password"]

        if not username:
            return "username is required"
        if not password:
            return "password is required"

        user = await cls.get_user(conn)
        if not user:
            return "invalid username"
        if not check_password_hash(password, user["password_hash"]):
            return "invalid password"
        else:
            return None

    @classmethod
    async def validate_register_data(cls, conn, data: Dict[str, str]) -> Union[str, None]:
        """
        Simple register data validation from POST request
        :param conn: DB pool
        :param data: login, pass
        :return: Specific error or None if check passed
        """
        username, password = data["username"], data["password"]

        if not username:
            return {"error": "username is required"}
        if not password:
            return {"error": "password is required"}
        user = await cls.get_user(conn)
        if user:
            return {"error": "This user already exists"}
        else:
            return None


class Players(BaseModel):
    """
    Players can register in game sessions, make moves and record results
    The game can be played by 2 players
    One of them is controlled by a computer
    """

    __tablename__ = "players"

    name = db.Column(db.String(64), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id", ondelete="CASCADE"))
    is_computer = db.Column(db.Boolean, default=False)

    @staticmethod
    async def get_player_by_name(conn, name: str):
        query = await conn.execute(Players.query.where(Players.name == name))
        user = await query.fetchone()
        return user


class GameInstance(BaseModel):
    """
    Store a game session
    """

    __tablename__ = "gameinstance"

    name = db.Column(db.String(64), primary_key=True)
    status = db.Column(db.String(64))
    next_turn = db.Column(db.String(64))


class Moves(BaseModel):
    """
    Store a history of all moves in all games here,
    each row has a gameid, a playerid, squarenum, and typeo
    """

    __tablename__ = "moves"

    id = db.Column(db.Integer, primary_key=True)
    square = db.Column(db.Integer)
    move_type = db.Column(db.String(10))
    game_name = db.Column(
        db.String(64), db.ForeignKey(f"{GameInstance.__tablename__}.name", ondelete="CASCADE")
    )
    player_name = db.Column(db.String(64), db.ForeignKey(f"{Players.__tablename__}.name", ondelete="CASCADE"))


class GamePlayerStats(BaseModel):
    """
    History of all games and the players tied to those games.
    Will store current score for each player in the game.
    useful for retrieving game statistics.
    """

    __tablename__ = "gameplayerstats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    move_type = db.Column(db.String(10), nullable=False)
    game_name = db.Column(
        db.String(64), db.ForeignKey(f"{GameInstance.__tablename__}.name", ondelete="CASCADE")
    )
    player_name = db.Column(db.String(64), db.ForeignKey(f"{Players.__tablename__}.name", ondelete="CASCADE"))
