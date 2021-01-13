from pathlib import Path
import datetime

import asyncpg
import pytoml
import discord
from discord.ext import commands
from loguru import logger

from .cogs import setup_cogs
from cogs.utils import log


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
    def __init__(self):
        self.description = "ooops"

        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            max_messages=100,
            intents=make_intents()
        )
        log.setup(str(Path(__name__).parent.parent / "logs"))
        self.pool = None
        self.session = None
        with open("./data/data.toml", 'r') as cfg:
            self.data = pytoml.load(cfg)
            logger.info("loaded config")
        setup_cogs(self)
        self.loop.run_until_complete(self.start_bot())

    @property
    def token(self):
        return self.data["BOT_TOKEN"]

    async def start_bot(self):
        await self.conn_db()

        launch_time = datetime.datetime.utcnow()
        logger.info("Bot Ready...")

    async def conn_db(self):
        try:
            self.pool = await asyncpg.create_pool(
                host=self.data['dbhost'],
                database=self.data['database'],
                user=self.data['user'],
                password=self.data['dbpassword'],
            )
            logger.info("Created Postgres Connection Pool")
        except Exception as e:
            logger.error(e)
