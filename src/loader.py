import asyncio

import discord
from discord.ext import commands
from loguru import logger

from src.db.base import create_db
from src.utils import log
from data.config import dstr, dbool

class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=dstr("PREFIX", "text"),
                         help_attrs=dict(hidden=True), pm_help=None,)

        self._main_loop = asyncio.get_event_loop()
        self.token = dstr("BOT_TOKEN", None)
        self._drop_after_restart = dbool("DROP_AFTER_RESTART", True)
        self._connected = asyncio.Event()

    async def on_ready(self):
        await self.wait_for_connected()
        logger.info("BOT READY")

    async def on_message(self, message: discord.Message):
        if message.author.bot or self.is_ready():
            return

        message.content.lower()
        await self.process_commands(message)

    async def wait_for_connected(self) -> None:
        await self.wait_until_ready()
        await self._connected.wait()

    async def run_itself(self):
        _loop = self._main_loop

        await create_db()
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



