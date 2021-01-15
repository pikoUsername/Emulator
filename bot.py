import random
from pathlib import Path

import aiohttp
import asyncpg
import pytoml
import discord
from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands
from loguru import logger

from cogs.utils import FileManager
from cogs.utils import log

LOGS_BASE_PATH = str(Path(__name__).parent.parent / "logs")

async def get_prefix(bot, message):
    return bot.data["PREFIX"]


def make_intents() -> discord.Intents:
    intents = discord.Intents.none()
    intents.emojis = True
    intents.messages = True
    intents.guild_messages = True
    intents.reactions = True
    return intents


class Bot(commands.AutoShardedBot):
    def __init__(self, loop=None):
        # self.loop = loop or asyncio.get_event_loop()

        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            description="Oops...",
            max_messages=100,
            intents=make_intents()
        )
        log.setup(LOGS_BASE_PATH)
        self.invoke_errors = 0
        self.session = aiohttp.ClientSession(loop=loop)
        self.pool = None
        self.launch_time = None
        self.fm = FileManager(self.pool, self.loop)

        self.extensions_ = [
            "admin", "cursor", "edit", "misc",
            "owner", "visual", "write", "events",
        ]
        with open("./data/data.toml", 'r') as cfg:
            self.data = pytoml.load(cfg)

    async def get_context(self, message, *, cls=commands.Context):
        """Get Context, ignores Guild"""
        if message.guild:
            return
        return await super().get_context(message, cls=cls)

    @property
    def token(self):
        return self.data['bot']["BOT_TOKEN"]

    async def send_with_webhook(self, text: str=None, *args, **kwargs):
        webhook = Webhook.from_url(
            self.data['bot']['onreadyurl'],
            adapter=AsyncWebhookAdapter(
                self.session)
        )
        await webhook.send(text, *args, **kwargs)

    def load_cogs(self):
        for extension in self.extensions_:
            try:
                self.load_extension(f"cogs.{extension}")
                logger.info(f"Loaded {extension}")
            except Exception as e:
                 logger.error(e)

    async def run_bot(self):
        self.load_cogs()
        try:
            await self.conn_db()
            await self.start(self.token)
        finally:
            await self.close_all()

    async def close_all(self):
        await self.pool.close()
        await self.close()

    @staticmethod
    def create_dsn(host: str, database: str, user: str, password: str, port: str):
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        return dsn

    async def conn_db(self):
        try:
            dsn = self.create_dsn(
                host=self.data['db']['dbhost'],
                database=self.data['db']['database'],
                user=self.data['db']['user'],
                password=self.data['db']['dbpassword'],
                port=self.data['db']['port'],
            )
            self.pool = await asyncpg.create_pool(dsn)
            logger.info("Created Postgres Connection Pool")
        except Exception as e:
            logger.error(e)
            raise e

    async def on_ready(self):
        random_text = [
            "Bot is Ready", "Bot isn't Readyn't",
            "is Ready Bot, Yes is it", "I gonna Fu...",
        ]

        await self.send_with_webhook(random.choice(random_text))

    async def create_error_letter(self, error, ctx: commands.Context):
        e = discord.Embed(
            title="Error Message: ",
            description=f"Your Error Ticket #{self.invoke_errors}"
        )
        e.add_field(
            name="Error",
            value=f"```{error}```",
            inline=False
        )
        e.set_footer(text="Error Message", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=e)
        self.invoke_errors += 1

        await self.send_with_webhook(embed=e)
