from sqlalchemy import Date, Table, Column, String, Boolean, Integer, DateTime, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
meta = MetaData()

# Base users model
users = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column("username", String(64), nullable=False, unique=True),
    Column("password_hash", String(128), nullable=False, unique=True),
    Column("is_admin", Boolean, default=False),
)

# Store a game session
gameinstance = Table(
    "game",
    meta,
    Column("name", String(64), primary_key=True, unique=True),
    Column("status", String(64)),
    Column("next_turn", String(64)),
)


# Store a history of all moves in all games here,
# each row has a gameid, a playerid, squarenum, and typeo
moves = Table(
    "moves",
    meta,
    Column("id", Integer, primary_key=True, unique=True),
    Column("square", Integer),
    Column("move_type", String(10)),
    Column("game_name", String(64), ForeignKey("game.name", ondelete="CASCADE")),
    Column("player_name", String(64), ForeignKey("users.username", ondelete="CASCADE")),
)


# History of all games and the players tied to those games.
# Will store current score for each player in the game.
# useful for retrieving game statistics.
gamestats = Table(
    "gamestats",
    meta,
    Column("id", Integer, primary_key=True, unique=True),
    Column("move_type", String(10), nullable=False),
    Column("game_name", String(100), ForeignKey("game.name", ondelete="CASCADE")),
    Column("player_name", String(100), ForeignKey("users.username", ondelete="CASCADE")),
)
