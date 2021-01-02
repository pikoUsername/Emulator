import asyncio
from typing import List
import os
import sys

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import errors
from loguru import logger

from src.utils import log
from data.config import LOGS_BASE_PATH, TOKEN, ERROR_CHANNEL, PREFIX, description
from src.utils.help import HelpFormat
from src.utils.file_manager import FileManager
from src.models import GuildAPI, UserApi
from src.models.base import db
from src.utils.cache import async_cache
from data.config import POSTGRES_URI


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
        self.drop_after_restart = False
        self._connected = asyncio.Event()
        self.APPLY_EMOJI = ':white_check_mark:'
        self.error_channel = Non
        self._extensions = [ # all extension for load
            "src.cogs.events",
            "src.cogs.redactor",
            # "src.cogs.info",
            "src.cogs.owner",
            "src.cogs.meta",
            "src.cogs.admin",
        ]
        self.count_commands = 0
        self.X_EMOJI = ":x:"
        self.pool = None

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

    async def get_prefix(self, message):
        return [f"{PREFIX} ", f"<@{self.user.id}> ", f"<@!{self.user.id}> ", PREFIX]

    async def close_db(self):
        bind = db.pop_bind()
        if bind:
            logger.info("Closing Postgres Connection")
            await bind.close()

    async def close_all(self):
        await self.session.close()
        await self.close_db()

    async def create_db(self):
        logger.info("creating database...")
        self.pool = await db.set_bind(POSTGRES_URI)

        await db.gino.create_all()

    async def on_ready(self):
        error_channel_id = ERROR_CHANNEL
        if error_channel_id:
            channel = self.get_channel(error_channel_id)
            if isinstance(channel, discord.TextChannel):
                self.error_channel = channel

        await self.wait_for_connected()
        logger.info("BOT READY")

    async def on_guild_remove(self, guild: discord.Guild):
        guild_ = await GuildAPI.get_guild(guild.id)
        if guild:
            try:
                await guild_.delete()
                await self.fm.delete_all_guild_files(guild_.id)
                logger.info(f"leaved from {guild_.guild_name}, and deleted thats guild folder")
            except Exception as e:
                bot_author = self.get_user(self.owner_id)
                if isinstance(bot_author, discord.DMChannel):
                    await bot_author.send(f"BOT REMOVED ALL GUILD's FILES {guild_.guild_name}")

                logger.exception(f"SHUTING DOWN:{e}")
                await self.close_all()

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

    async def on_command_error(self, ctx: commands.Context, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            logger.exception(f"{err}, {sys.exc_info()}")

            # await self.error_channel.send(file=file)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{err}", delete_after=30)

        elif isinstance(err, errors.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title=f"Fail {self.X_EMOJI}",
                description="Permission ERROR",
            ))

        elif isinstance(err, errors.CheckFailure):
            await ctx.send(embed=discord.Embed(
                title=f"Fail {self.X_EMOJI}",
                description="You cant made this",
            ))

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...", delete_after=30)

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cool down... try again in {err.retry_after:.2f} seconds.", delete_after=30)

        elif isinstance(err, errors.CommandNotFound):
            pass

        elif isinstance(err, errors.NoPrivateMessage):
            await ctx.send(embed=discord.Embed(title="Private message Not work",
                                               description="Bot work only in guild channels")
                           )

        else:
            logger.exception(err)
            await self.send_error(ctx, err)

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
            await self.create_db()
            if self.drop_after_restart:
                logger.warning("Removing all files from files/ directory!")
                await self.fm.delete_all_guild_files()
            await self.start(self.token)
        except Exception as e:
            logger.exception("CRITICAL ERROR")
            raise e
        finally:
            await self.close_all()


