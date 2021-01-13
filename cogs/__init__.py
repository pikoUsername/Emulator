import os

from . import utils

__all__ = ("utils",)


def setup_cogs(bot):
    for file in os.listdir("/"):
        if file.endswith(".py"):
            if file == "__init__.py":
                pass
            else:
                name = file[:-3]
                bot.load_extension(f"cogs.{name}")
