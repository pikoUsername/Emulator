from typing import List

from typing import TypeVar, Type

import contextvars
import sqlalchemy as sa
from gino import Gino


db = Gino()
T = TypeVar('T')

# https://github.com/aiogram/aiogram/blob/dev-2.x/aiogram/utils/mixins.py
class ContextInstanceMixin:
    def __init_subclass__(cls, **kwargs):
        cls.__context_instance = contextvars.ContextVar(f'instance_{cls.__name__}')
        return cls

    @classmethod
    def get_current(cls: Type[T], no_error=True) -> T:
        if no_error:
            return cls.__context_instance.get(None)
        return cls.__context_instance.get()

    @classmethod
    def set_current(cls: Type[T], value: T):
        if not isinstance(value, cls):
            raise TypeError(f'Value should be instance of {cls.__name__!r} not {type(value).__name__!r}')
        cls.__context_instance.set(value)


# https://github.com/aiogram/bot/blob/master/app/models/db.py nooooooooooo, i copied code ;(
class BaseModel(db.Model, ContextInstanceMixin):
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

