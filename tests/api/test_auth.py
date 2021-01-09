from http import HTTPStatus

from server.models.entities import User

TESTUSER = {
    "username": "testuser",
    "password": "12345678",
    "confirm": "12345678",
}


async def test_auth_home_page(api_client):
    resp = await api_client.get("/auth/")
    assert resp.status == HTTPStatus.OK


async def test_user_signup(api_client):
    resp = await api_client.post(
        "/auth/login",
        {"username": TESTUSER["username"], "password": TESTUSER["password"], "confirm": TESTUSER["confirm"]},
    )
    assert resp.status == HTTPStatus.OK

    async with api_client.app["db"] as conn:
        user = await User.get_user(conn)
        assert user["username"] == TESTUSER["username"]


async def test_user_login(api_client):
    resp = await api_client.post(
        "/auth/login", {"username": TESTUSER["username"], "password": TESTUSER["password"]}
    )
    assert resp.status == HTTPStatus.OK

    async with api_client.app["db"] as conn:
        user = await User.get_user(conn)
        assert user["disabled"] is False


async def test_user_logout(api_client):
    resp = await api_client.get("/auth/logout")
    assert resp.status == HTTPStatus.OK

    async with api_client.app["db"] as conn:
        user = await User.get_user(conn)
        assert user["disabled"]
