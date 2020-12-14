import asyncio
from typing import Optional
import os
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv

from src.db.guild import GuildAPI, Guild
from src.db.user import User
from src.utils.errors import UserNotFound

load_dotenv()

LOGS_BASE_PATH = str(Path(__name__).parent.parent / "logs")

def dstr(key: str, default: Optional[str] = None):
    return str(os.getenv(key, default))

def dint(key: str, default: Optional[int] = 0):
    return os.getenv(key, default)

def dbool(key: str, default: Optional[bool]=True):
    return os.getenv(key, default)

class ConfigProxy:
    def __init__(self, ctx):
        self.ready_event = asyncio.Event()
        self._data = {}

    async def wait_until_ready(self):
        await self.ready_event.wait()

    async def update(self, data=None, **kwargs):
        await self.update_guild_config(**kwargs)

    async def _check_user(self):
        user = User.get_current().id

        if not user:
            return

        return user

    async def update_guild_config(self, *args, **kwargs):
        await self._check_user()

        # here update config of user

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        await self._check_user()

        self._data[key] = value

    def __delitem(self, key):
        await self._check_user()

        del self._data[key]

class UserConfig(ConfigProxy):
    def __init__(self, ctx):
        if not ctx:
            self.ctx = commands.Context
        else:
            self.ctx = ctx
        super().__init__(ctx)

    def proxy(self):
        return ConfigProxy(self)

