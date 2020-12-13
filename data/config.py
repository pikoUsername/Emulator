import asyncio
from typing import Optional
import os

from discord.ext import commands
from dotenv import load_dotenv

from src.utils.db_api.api.guild import GuildAPI
from src.utils.misc.errors import UserNotFound

load_dotenv()

def dstr(key: str, default: Optional[str] = None):
    return str(os.getenv(key, default))

def dint(key: str, default: Optional[int] = 0):
    return os.getenv(key, default)

def dbool(key: str, default: Optional[bool]=True):
    return os.getenv(key, default)

class UserConfigProxy:
    def __init__(self, ctx):
        self.ready_event = asyncio.Event()
        self._data = {}
        self.ctx: commands.Context = ctx

    async def wait_until_ready(self):
        await self.ready_event.wait()

    async def update(self, data=None, **kwargs):
        await self._check_user()
        await self.update_user_config(**kwargs)

    async def update_user_config(self, *args, **kwargs):
        await self._check_user()

        user_id = self.ctx.message.author.id


    async def _check_user(self, *args, **kwargs):
        ctx = self.ctx

        guild_model = await GuildAPI.get_guild(ctx.guild.id)

        if guild_model is None:
            raise UserNotFound("This User Dont exists in Bot DB!", self.ctx)


    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        await self._check_user()

        self._data[key] = value

    def __delitem(self, key):
        await self._check_user()

        del self._data[key]

class UserConfig:
    def __init__(self, ctx):
        self.ctx = ctx

    def proxy(self):
        return UserConfigProxy(self)

