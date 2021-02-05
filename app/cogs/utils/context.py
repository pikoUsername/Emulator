import asyncpg
from typing import Optional
from discord.ext.commands import Context

from .db.postgres import PostgresConnection

__all__ = ("CustomContext",)


class CustomContext(Context):
    """
    For db contact
    """
    _make_request = PostgresConnection._make_request

    async def get_user(self, user_id: int) -> Optional[asyncpg.Record]:
        sql = "SELECT u.* FROM users as users WHERE user_id = $1;"
        user = await self._make_request(sql, (user_id), fetch=True)
        return user
