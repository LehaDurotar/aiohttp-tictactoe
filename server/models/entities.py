from typing import Dict, Union

from server.db.database import TimedBaseModel, db
from server.db.security import check_password_hash, generate_password_hash


class Users(TimedBaseModel):
    """
    # Base users model
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, unique=True, index=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)

    @staticmethod
    async def get_user_by_name(conn, username: str):
        query = await conn.execute(Users.query.where(Users.username == username))
        user_name = await query.fetchone()
        return user_name

    @staticmethod
    async def create_user(conn, user_data: dict) -> None:
        """
        Create new record in DB
        """
        username, password = user_data["username"], user_data["password"]
        hashed_pass = generate_password_hash(password)
        query = Users.insert().values(username=username, password_hash=hashed_pass)
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

        user = await cls.get_user_by_name(conn, username)
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
            return "username is required"
        if not password:
            return "password is required"
        user = await cls.get_user_by_name(conn, username)
        if user:
            return "This user already exists"
        else:
            return None


class GameInstance(TimedBaseModel):
    """
    Store a game session
    """

    __tablename__ = "gameinstance"

    name = db.Column(db.String(64), primary_key=True, unique=True)
    status = db.Column(db.String(64))
    next_turn = db.Column(db.String(64))


class Moves(TimedBaseModel):
    """
    Store a history of all moves in all games here,
    each row has a gameid, a playerid, squarenum, and typeo
    """

    __tablename__ = "moves"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    square = db.Column(db.Integer)
    move_type = db.Column(db.String(10))
    game_name = db.Column(
        db.String(64), db.ForeignKey(f"{GameInstance.__tablename__}.name", ondelete="CASCADE")
    )
    player_name = db.Column(
        db.String(64), db.ForeignKey(f"{Users.__tablename__}.username", ondelete="CASCADE")
    )


class GamePlayerStats(TimedBaseModel):
    """
    History of all games and the players tied to those games.
    Will store current score for each player in the game.
    useful for retrieving game statistics.
    """

    __tablename__ = "gameplayerstats"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    move_type = db.Column(db.String(10), nullable=False)
    game_name = db.Column(
        db.String(64), db.ForeignKey(f"{GameInstance.__tablename__}.name", ondelete="CASCADE")
    )
    player_name = db.Column(
        db.String(64), db.ForeignKey(f"{Users.__tablename__}.username", ondelete="CASCADE")
    )
