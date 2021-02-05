from typing import Type, TypeVar

import contextvars

T = TypeVar("T")


class ContextInstanceMixin:
    def __init_subclass__(cls, **kwargs):
        cls.__context_mixin = contextvars.ContextVar(f'context_{cls.__name__}')
        return cls

    @classmethod
    def get_current(cls: Type[T]) -> T:
        return cls.__context_mixin.get()

    @classmethod
    def set_current(cls: Type[T], value: T):
        if not isinstance(value, cls):
            raise TypeError(f'Value should be instance of'
                            f' {cls.__name__!r} not {type(value).__name__!r}')
        cls.__context_mixin.set(value)
