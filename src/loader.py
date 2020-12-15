import asyncio

import discord
from discord.ext import commands
from loguru import logger


from src.db.base import create_db
from src.utils import log
from data.config import dstr, dbool, dlist

class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=f"{dstr('PREFIX', 'text')} ",
                         help_attrs=dict(hidden=True), pm_help=None,
                         owner_ids=dlist("OWNERS", 0)
                         )

        self.token = dstr("BOT_TOKEN", None)
        self._drop_after_restart = dbool("DROP_AFTER_RESTART", True)
        self._connected = asyncio.Event()
        self._extensions = [
            "src.cogs.events",
            "src.cogs.redactor",
            "src.cogs.info",
        ]

    def __repr__(self):
        return "<Bot>"

    async def on_ready(self):
        await self.wait_for_connected()
        logger.info("BOT READY")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        logger.info("msg here processing")
        await self.process_commands(message)

    async def wait_for_connected(self) -> None:
        await self.wait_until_ready()
        await self._connected.wait()

    async def on_message_edit(self, before, after):
        """Handler for edited messages, re-executes commands"""
        if before.content != after.content:
            await self.on_message(after)

    async def run_itself(self):
        await create_db()
        log.setup()

        # setup stuff
        for extension in self._extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                logger.exception(e)
                return

        try:
            await create_db(self._drop_after_restart)
            await self.start(self.token)
        except KeyboardInterrupt:
            logger.warning("Goodbye!")
        except Exception as e:
            logger.exception(f"ERROR: {e}")
        finally:
            try:
                await self.logout()
            except asyncio.TimeoutError:
                pass



