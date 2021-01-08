from typing import Dict

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
    async def get_user(cls, conn) -> Dict[str, str]:
        """
        Returns the currently registered
        :param conn: pg.sa connection
        :return: user data
        """
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
    async def remember(cls, conn, password) -> None:
        """
        Set simple db session with the currently registered user
        :param conn: pg.sa connection
        :param password:
        """
        user = await cls.get_user(conn)

        if not user:
            raise ValueError("This user does not exist")

        if not check_password_hash(password, user["password_hash"]):
            raise ValueError("Invalid password")

        query = cls.update.values(username=user["username"], disabled=False)
        await conn.execute(query)

    @classmethod
    async def forget(cls, conn) -> None:
        """
        Close login session
        :param conn: pg.sa connection
        """
        user = await cls.get_user(conn)
        query = cls.update.values(username=user["username"], disabled=True)
        await conn.execute(query)

    @classmethod
    async def create_user(cls, conn, user_data: Dict[str, str]) -> None:
        """
        Creates a user record in the database
        :param conn: pg.sa connection
        :param user_data: login, pass, confirm pass
        """
        user = await User.get_user(conn)
        if user:
            raise ValueError("This user already exists")
        username, password = user_data["username"], user_data["password"]
        hashed_pass = generate_password_hash(password)
        query = cls.insert().values(username=username, password_hash=hashed_pass)
        await conn.execute(query)


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

    @classmethod
    async def get_player_by_name(cls, conn, name: str):
        query = await conn.execute(cls.query.where(cls.name == name and not cls.is_computer))
        player = await query.fetchone()
        return player


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
