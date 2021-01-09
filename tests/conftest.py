import pytest
from yarl import URL

from server.settings import POSTGRES_URI


@pytest.fixture(scope="session")
def pg_url():
    """
    Provides base PostgreSQL URL for creating temporary databases.
    """
    return URL(POSTGRES_URI)
