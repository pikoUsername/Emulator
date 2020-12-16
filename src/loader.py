import asyncio
from typing import List
import os

import discord
from discord.ext import commands
from discord.ext.commands import errors
from loguru import logger

from src.utils import log
from data.config import dstr, dbool, dlist
from data.config import LOGS_BASE_PATH
from src.utils.help import HelpFormat
from src.utils.file_manager import FileManager
from src.db.user import UserApi
from data.base_cfg import POSTGRES_URI
from src.db import db

class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=f"{dstr('PREFIX', 'text')} ",
                         help_attrs=dict(hidden=True), pm_help=None,
                         owner_ids=dlist("OWNERS", 0))

        self.help_command = HelpFormat()
        self.fm: FileManager = FileManager(self.loop) # Shortcut
        self.uapi = UserApi() # shortcut
        self.token = dstr("BOT_TOKEN", None)
        self._drop_after_restart = dbool("DROP_AFTER_RESTART", True)
        self._connected = asyncio.Event()
        self.APPLY_EMOJI = ':white_check_mark:'
        self.error_channel = None
        self._extensions = [ # all extension for load
            "src.cogs.events",
            "src.cogs.redactor",
            "src.cogs.info",
            "src.cogs.owner",
        ]
        self.connected_to_database = asyncio.Event()
        self.connected_to_database.set()
        self.db = self.database = self.database_connection_pool = None
        self.POSTGRES_URI = POSTGRES_URI

    def __repr__(self):
        return f"<Bot name='{self.user.name}', id='{self.user.id}'>"

    async def create_db(self):
        logger.info("creating database...")
        await db.set_bind(self.POSTGRES_URI)

        await db.gino.drop_all()
        await db.gino.create_all()

    async def on_ready(self):
        error_channel_id = dstr("ERROR_CHANNEL", None)
        if error_channel_id:
            channel = self.get_channel(error_channel_id)
            if isinstance(channel, discord.TextChannel):
                self.error_channel = channel

        await self.wait_for_connected()
        logger.info("BOT READY")

    @property
    def last_log(self) -> List:
        """
        Get last log from /logs/ folder

        :return:
        """
        logs_list: List = os.listdir(LOGS_BASE_PATH)
        full_list = [os.path.join(LOGS_BASE_PATH, i) for i in logs_list]
        time_sorted_list: List = sorted(full_list, key=os.path.getmtime)

        return time_sorted_list[-1]

    @property
    def all_logs(self):
        """
        get all logs from logs/ folder

        :return:
        """
        return os.listdir(LOGS_BASE_PATH)

    async def on_command_error(self, ctx: commands.Context, err):
        file = self.get_last_log_file()
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            logger.exception(err)

            await self.error_channel.send(file=file)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{err}", delete_after=30)

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...", delete_after=30)

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cool down... try again in {err.retry_after:.2f} seconds.", delete_after=30)

        elif isinstance(err, errors.CommandNotFound):
            pass

        elif isinstance(err, errors.NoPrivateMessage):
            pass

        else:
            await self.error_channel.send(file=file)

    async def get_last_log_file(self):
        """
        gets logs from directory /logs/  and return it
        in file format

        :return:
        """

        try:
            last_log = str(self.last_log)
        except Exception as e:
            last_log = None
            logger.error(f"untracked exception: {e}")

        if not last_log:
            return
        try:
            with open(last_log, "r") as file:
                return file
        except Exception as e:
            logger.error(f"Untracked exception: {e}")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.process_commands(message)

    async def wait_for_connected(self) -> None:
        await self.wait_until_ready()
        await self._connected.wait()

    async def on_message_edit(self, before, after):
        """Handler for edited messages, re-executes commands"""
        if before.content != after.content:
            await self.on_message(after)

    async def run_itself(self):
        log.setup()

        # setup stuff
        for extension in self._extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                logger.exception(e)
                return

        self.load_extension('jishaku')

        await self.create_db()
        await self.start(self.token)



