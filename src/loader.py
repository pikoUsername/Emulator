import asyncio

import typing
import discord
from discord.ext import commands
from loguru import logger

from data.config import dstr, dbool
from src.db.base import create_db
from data.config import UserConfig
from src.utils import log
from src.db.guild import Guild
from src.db.user import User

class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        self.storage = kwargs.get("storage")
        super().__init__(*args, **kwargs)

        self._main_loop = asyncio.get_event_loop()
        self.token = dstr("BOT_TOKEN", None)
        self._drop_after_restart = dbool("DROP_AFTER_RESTART", True)
        self._connected = asyncio.Event()
        self.config = UserConfig

    async def on_message(self, message: discord.Message):
        if message.author.bot or self.is_ready():
            return

        await self.process_commands(message)

    async def wait_for_connected(self) -> None:
        await self.wait_until_ready()
        await self._connected.wait()
        await self.config.wait_until_ready()

    async def run_itself(self):
        _loop = self._main_loop

        log.setup()

        try:
            await create_db(self._drop_after_restart)
            _loop.run_until_complete(self.start(self.token))
        except KeyboardInterrupt:
            logger.warning("Goodbye!")
        except Exception as e:
            logger.exception(f"ERROR: {e}")
        finally:
            try:
                await self.logout()
                _loop.close()
            except asyncio.TimeoutError:
                pass



