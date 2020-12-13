import datetime
from typing import List

import sqlalchemy as sa
from gino import Gino

db = Gino()

# https://github.com/aiogram/bot/blob/master/app/models/db.py
class BaseModel(db.Model):
    __abstract__ = True

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

async def create_db(drop: bool=True):
    await db.set_bind()

    if drop:
        await db.gino.drop_all()
    await db.gino.create_all