import asyncpg
from typing import Optional
from discord.ext.commands import Context

from .db.postgres import PostgresConnection

__all__ = ("DBContext",)


class DBContext(Context, PostgresConnection):
    async def get_user(self, user_id: int) -> Optional[asyncpg.Record]:
        sql = "SELECT u.user_id, u.name, u.guilds FROM users as users WHERE user_id = $1;"
        user = await self._make_request(sql, (user_id,), fetch=True)
        return user
