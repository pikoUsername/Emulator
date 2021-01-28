import asyncio
from typing import List
import os

import aiohttp
import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from gino import GinoEngine
from loguru import logger

from src.config import (
    LOGS_BASE_PATH,
    TOKEN,
    ERROR_CHANNEL,
    description,
    PREFIX,
)
from .utils.help import HelpFormat
from .utils.file_manager import FileManager
from .models import User
from .models.base import db
from .utils import async_cache
from .utils.spammer import Spammer
from .config import POSTGRES_URI, WEB_HOOK_URL


class Bot(commands.AutoShardedBot, ):
    def __init__(self):
        super().__init__(command_prefix=PREFIX, description=description,
                         help_attrs=dict(hidden=True), pm_help=None)

        self.spammer: Spammer = Spammer(self)
        self.help_command = HelpFormat()
        self.fm: FileManager = FileManager(self.loop)
        self.token = TOKEN
        self.uapi = User()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self._connected = asyncio.Event()
        self.APPLY_EMOJI = '\n{white check mark}'
        self._error_channel = None
        self.extensions_ = [
            "src.cogs.events",
            "src.cogs.redactor",
            "src.cogs.info",
            "src.cogs.owner",
            "src.cogs.meta",
            "src.cogs.admin",
        ]
        self.count_commands = 0
        self.X_EMOJI = ":x:"
        self.pool: GinoEngine
        self.prefdict = {}
        self.error_ids = {
            'guild_id': 775955280625926144,
            'channel_id': 794125321389342790,
        }

    async def setup_stuff(self):
        await self.init_db()
        for cog in self.extensions_:
            try:
                self.load_extension(f'{cog}')
            except Exception as e:
                logger.error(e)

    @async_cache()
    async def send_error(self, ctx: commands.Context, err):
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

        await self.error_channel.send(embed=embed)
        return await ctx.send("Success, Sended to Error Channel")

    async def close_db(self):
        try:
            bind = db.pop_bind()
        except AttributeError:
            bind = None
        if bind:
            logger.info("Closing Postgresql Connection")
            await bind.close()

    async def close_all(self):
        await self.close()
        await self.close_db()

    @property
    def error_channel(self) -> discord.TextChannel:
        if self._error_channel is None:
            err_ch = self.get_guild(self.error_ids['guild_id'])\
                .get_channel(self.error_ids['channel_id'])
            if not isinstance(err_ch, discord.TextChannel):
                raise TypeError("Canont Set error_channel with 'TextChannel'")
        return self._error_channel

    @error_channel.setter
    def error_channel(self, item):
        if not isinstance(item, discord.TextChannel):
            raise TypeError("ITem is not isinstance of 'TextChannel'")
        self._error_channel = item

    @error_channel.deleter
    def error_channel(self):
        self.error_channel = None

    async def conn_db(self):
        logger.info("Connecting Database...")

        self.pool = await db.set_bind(POSTGRES_URI, loop=self.loop)

    async def create_db(self):
        logger.info("creating database...")
        await db.gino.create_all(bind=self.pool)

    async def on_ready(self):
        error_channel_id = ERROR_CHANNEL
        if error_channel_id:
            channel = self.get_channel(error_channel_id)
            if isinstance(channel, discord.TextChannel):
                self._error_channel = channel

        logger.info("BOT READY")
        await self.postready()
        await self.wait_for_connected()

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
        self.count_commands += 1
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
        await self.setup_stuff()
        try:
            await self.start(self.token)
        except KeyboardInterrupt:
            logger.info("GoodBye")

    def __del__(self):
        self.loop.run_until_complete(self.close_all())
        self.loop.run_until_complete(self.session.close())
