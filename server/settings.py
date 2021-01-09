import os
import uuid
import pathlib
from types import SimpleNamespace
from contextlib import contextmanager

import yaml
from yarl import URL
from sqlalchemy_utils import drop_database, create_database

from server import __name__ as project_name
from alembic.config import Config

BASE_DIR = pathlib.Path(__file__).parent.parent
PROJECT_PATH = pathlib.Path(__file__).parent.parent.resolve()
config_path = BASE_DIR / "config" / "dev_example.yaml"


def get_config(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    return data


cfg = get_config(config_path)
db_cfg = cfg["postgres"]
POSTGRES_URI = f"postgresql://{db_cfg['user']}:{db_cfg['password']}@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['database']}"
DEFAULT_PG_URL = "postgresql://tictac:postgres@localhost/tictactoedev_db"


@contextmanager
def tmp_database(db_url: URL, suffix: str = "", **kwargs):
    tmp_db_name = "_".join([uuid.uuid4().hex, project_name, suffix])
    tmp_db_url = str(db_url.with_path(tmp_db_name))
    create_database(tmp_db_url, **kwargs)

    try:
        yield tmp_db_url
    finally:
        drop_database(tmp_db_url)


def make_alembic_config(cmd_opts, base_path: str = PROJECT_PATH) -> Config:
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option("script_location", os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: str = None) -> Config:
    """
    Provides Python object, representing alembic.ini file.
    """
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_url=pg_url,
        raiseerr=False,
        x=None,
    )

    return make_alembic_config(cmd_options)
