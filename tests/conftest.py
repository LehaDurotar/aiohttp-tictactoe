import sys

sys.path.append('server')

import pytest
from server.main import init_app


@pytest.fixture
async def cli(loop, test_client):
    app = init_app()
    return await test_client(app)
