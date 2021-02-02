from typing import Optional, Union, List
import datetime

import sqlalchemy as sa
from gino import Gino, GinoConnection
from sqlalchemy import sql

db = Gino()

__all__ = ("db", "TimedBaseModel", "BaseModel")


async def make_request(
        query: str,
        params: Union[Optional[tuple], str, List[str]] = None,
        multi: bool = False,
        fetch: bool = False,
):
    async with db.acquire() as conn:
        conn: GinoConnection = conn
        async with conn.transaction():
            if fetch:
                if multi:
                    res = await conn.all(query, *params if len(params) != 1 else params)
                else:
                    res = await conn.first(query, *params if len(params) != 1 else params)
                return res


class BaseModel(db.Model):
    __abstract__ = True
    query: sql.Select

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.primary_key.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = db.Column(db.DateTime(True), server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime(True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=db.func.now(),
    )
