import asyncio
import typing
from typing import List
import os
import sys

import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from loguru import logger

from src.utils import log
from data.config import LOGS_BASE_PATH, TOKEN, ERROR_CHANNEL, PREFIX, description
from src.utils.help import HelpFormat
from src.utils.file_manager import FileManager
from src.models import UserApi
from src.models.base import db
from src.utils.cache import async_cache
from data.config import POSTGRES_URI, WEB_HOOK_URL


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, description=description,
                         help_attrs=dict(hidden=True), pm_help=None)

        self.owner_id = 426028608906330115
        self.help_command = HelpFormat()
        self.fm: FileManager = FileManager(self.loop) # Shortcut
        self.token = TOKEN
        self.uapi: UserApi = UserApi()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self._connected = asyncio.Event()
        self.APPLY_EMOJI = '\n{white check mark}'
        self.error_channel = None
        self._extensions = [ # all extension for load
            "src.cogs.events",
            "src.cogs.redactor",
            "src.cogs.info",
            "src.cogs.owner",
            "src.cogs.meta",
            "src.cogs.admin",
        ]
        self.count_commands = 0
        self.X_EMOJI = ":x:"
        self.pool = None
        self.prefixes = {}

    @async_cache()
    async def send_error(self, ctx: commands.Context, err):
        error_log_channel = self.get_guild(775955280625926144).get_channel(794125321389342790)

        embed = discord.Embed(
            title="Something went wrong...",
            description=f"```py\nAn Error Occurred:\n{err}\n```",
        )
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}", icon_url=ctx.author.avatar_url
        )
        if ctx.guild:
            cmd = (
                "None"
                if isinstance(ctx.command, type(None))
                else ctx.command.qualified_name
            )
            embed.set_thumbnail(url=ctx.guild.icon_url_as(size=512))
            embed.add_field(
                name="Key Information:\n",
                value=f"Channel: {ctx.channel} {ctx.channel.id}\n"
                f"Guild: {ctx.guild} {ctx.guild.id}\n"
                f"Command: {cmd}\n"
                f"Message Content: {ctx.message.content}",
            )

        await error_log_channel.send(embed=embed)
        return await ctx.send("Success, Sended to Error Channel")

    def set_prefix(self, guild: discord.Guild, prefix: str):
        if len(prefix) < 200:
            return False

        self.prefixes[guild.id] = prefix

    async def get_prefix(self, message):
        prefix = [f"<@{self.user.id}> ", f"<@!{self.user.id}> ", PREFIX, self.prefixes.get(message.guild.id, default=PREFIX)]
        return prefix

    async def close_db(self):
        bind = self.pool
        if bind:
            logger.info("Closing Postgres Connection")
            await bind.close()

    async def close_all(self):
        await self.session.close()
        await self.close_db()

    async def conn_db(self):
        logger.info("Connecting to Database...")

        self.pool = await db.set_bind(POSTGRES_URI)

    async def create_db(self):
        logger.info("creating database...")
        await db.gino.create_all(bind=self.pool)

    async def on_ready(self):
        error_channel_id = ERROR_CHANNEL
        if error_channel_id:
            channel = self.get_channel(error_channel_id)
            if isinstance(channel, discord.TextChannel):
                self.error_channel = channel

        logger.info("BOT READY")
        await self.wait_for_connected()
        await self.postready()

    async def postready(self):
        webhook = Webhook.from_url(
            WEB_HOOK_URL,
            adapter=AsyncWebhookAdapter(
                self.session))
        await webhook.send('Bot is Online')

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

    async def process_command(self, message):
        ctx = await self.get_context(message, cls=commands.Context)
        if not ctx.command:
            return

        if message.author.bot:
            return

        await self.invoke(ctx)

    async def on_command(self, ctx: commands.Context):
        self.count_commands =+ 1
        try:
            logger.info(f"Activated command {ctx.command.name}, user: {ctx.author.name}, guild: {ctx.guild.name}")
        except AttributeError:
            logger.info(f"Activated command {ctx.command.name}, user: {ctx.author.name}")

    def get_last_log_file(self):
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

    async def init_db(self):
        await self.conn_db()
        await self.create_db()

    async def run_itself(self):
        log.setup()
        # setup stuff
        for extension in self._extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                logger.error(str(e))
                raise e

        try:
            await self.init_db()
            await self.start(self.token)
        except Exception as e:
            logger.exception("CRITICAL ERROR")
            raise e
        finally:
            await self.close_all()
