from typing import TypeVar, Type, List, Union, Any, Dict, Optional

import asyncpg

from .base import RawConnection
from ....bot import Bot  # yes

__all__ = ("PostgresConnection",)

T = TypeVar("T")


class PostgresConnection(RawConnection):
    pool: asyncpg.pool.Pool

    @staticmethod
    async def __make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            retries_count: int = 5
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        if not PostgresConnection.connection_pool:
            bot = Bot.get_current()
            PostgresConnection.connection_pool = await asyncpg.create_pool(
                **bot.data['db']
            )
        async with PostgresConnection.connection_pool.acquire() as conn:
            conn: asyncpg.Connection = conn
            async with conn.transaction():
                if fetch:
                    if mult:
                        r = await conn.fetchval(sql, *params)
                    else:
                        r = await conn.fetch(sql, *params)
                    return r
                else:
                    await conn.execute(sql, *params)

    @staticmethod
    def _convert_to_model(data: Optional[dict], model: Type[T]) -> Optional[T]:
        if data is not None:
            return model(**data)
        else:
            return None
        
    @staticmethod
    async def _make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            model_type: Type[T] = None
    ):
        raw = await PostgresConnection.__make_request(sql, params, fetch, mult)
        if raw is None:
            if mult:
                return []
            else:
                return None
        else:
            if mult:
                if PostgresConnection:
                    return [PostgresConnection._convert_to_model(i, model_type) for i in raw]
                else:
                    return list(raw)
            else:
                if model_type:
                    return PostgresConnection._convert_to_model(raw, model_type)
                else:
                    return raw

