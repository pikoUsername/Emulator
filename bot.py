import random
from pathlib import Path

import aiohttp
import pytoml
import discord
from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands
from loguru import logger

from cogs.utils import log
from cogs.utils.mixins import ContextInstanceMixin

LOGS_BASE_PATH = str(Path(__name__).parent.parent / "logs")


async def get_prefix(bot, message):
    # need to do custom prefix for every user
    return bot.data['bot']["PREFIX"]


def make_intents() -> discord.Intents:
    # i used Intent class, not a none intent, it was a bad idea ;(
    intents = discord.Intents.none()
    intents.emojis = True
    intents.messages = True
    intents.guild_messages = True
    intents.reactions = True
    return intents


class Bot(commands.AutoShardedBot, ContextInstanceMixin):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            intents=make_intents()
        )
        # setup in __init__
        log.setup(LOGS_BASE_PATH)

        # counter for errors, and error ticket
        # its bad, but it s only available method
        self.invoke_errors = 0
        # uptime
        self.launch_time = None

        # extensions for setup in bot
        self.extensions_ = [
            "admin", "edit", "misc", "owner",
            "visual", "write", "events",
        ]
        with open("./data/data.toml", 'r') as cfg:
            self.data = pytoml.load(cfg)

    async def get_context(self, message, *, cls=commands.Context):
        # bot cant be used in guilds, it s not working without this
        # so fuck
        if message.guild:
            return
        return await super().get_context(message, cls=cls)

    @property
    def token(self):
        # useless property
        return self.data['bot']["BOT_TOKEN"]

    @token.setter
    def token(self):
        import warnings
        warnings.warn(
            "Token is READ ONLY!"
        )

    @token.deleter
    def token(self):
        self.token = None

    async def send_with_webhook(self, *args, **kwargs):
        # maybe its crash everything, but i dk
        webhook = Webhook.from_url(
            self.data['bot']['onreadyurl'],
            adapter=AsyncWebhookAdapter(
                aiohttp.ClientSession()))
        await webhook.send(*args, **kwargs)

    async def run_bot(self):
        for extension in self.extensions_:
            try:
                self.load_extension(f"cogs.{extension}")
                logger.info(f"Loaded {extension}")
            except Exception as e:
                # if exception cathced, bot running dont stop
                logger.error(e)

        await self.start(self.token)

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
