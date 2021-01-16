from contextlib import suppress
from typing import List

import sqlalchemy as sa
from sqlalchemy import sql
from loguru import logger
from gino import Gino, UninitializedError


db = Gino()


class BaseModel(db.Model):
    __abstract__ = True
    query: sql.Select

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.columns
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
        db.DateTime(True), default=db.func.now(), onupdate=db.func.now(), server_default=db.func.now()
    )


def create_uri(bot):
    db_data = bot.data['db']
    uri = "postgresql://{}:{}@{}:{}/{}".format(
        db_data['user'],
        db_data['dbpassword'],
        db_data['dbhost'],
        db_data['port'],
        db_data['database'],
    )
    return uri


async def create_bind(bot):
    dsn = create_uri(bot)

    bind = await db.set_bind(dsn)
    bot.bind = bind
    logger.info("Created Postgres connection")

    await db.gino.create_all(bind=bind)

    return bind


async def close_conn():
    with suppress(UninitializedError):
        logger.info('Closing a database connection')
        await db.pop_bind().close()
