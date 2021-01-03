from aiohttp_security.abc import AbstractAuthorizationPolicy

from .database import get_user_by_name


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def authorized_userid(self, identity):
        async with self.db_pool.acquire() as conn:
            user = await get_user_by_name(conn, identity)
            if user:
                return identity

        return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return True
