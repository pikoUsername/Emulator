import asyncio

import discord
from discord.ext import commands

from data.config import dstr, dbool
from src.utils.db_api.models.base import create_db

class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._main_loop = asyncio.get_event_loop()
        self.token = dstr("BOT_TOKEN", None)
        self._drop_after_restart = dbool("DROP_AFTER_RESTART", True)

    async def on_message(self, message: discord.Message):
        if message.author.bot or self.is_ready():
            return

        await self.process_commands(message)

    async def run_itself(self):
        _loop = self._main_loop

        await create_db(self._drop_after_restart)

        try:

            _loop.run_until_complete()




