import random
from pathlib import Path
from typing import Optional

import aiohttp
import pytoml
import discord
from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands
from loguru import logger

from app.cogs.utils import log
from app.cogs.utils import CustomContext
from app.cogs.utils import ContextInstanceMixin

LOGS_BASE_PATH = str(Path(__name__).parent.parent.parent / "logs")

__all__ = ("Bot",)


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
            command_prefix=self.get_prefix,
            intents=make_intents()
        )
        # setup in __init__
        log.setup(LOGS_BASE_PATH)

        # counter for errors, and error ticket
        # its bad, but it s only available method
        self.invoke_errors = 0
        # uptime
        self.launch_time = None
        self.extensions_ = None
        with open("data/data.toml") as cfg:
            self.data = pytoml.load(cfg)

    async def get_context(self, message, *, cls=CustomContext):
        # bot cant be used in guilds, it s not working without this
        # so fuck
        if message.guild:
            return
        return await super().get_context(message, cls=cls)

    async def get_prefix(self, message):
        return self.data['bot']['PREFIX']

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

    @property
    def file_path(self) -> Optional[Path]:
        up = self.data['bot']['BASE_PATH']
        if up is None or up == " ":
            raise TypeError("BASE_PATH is Empty")
        res = Path(up)
        return res

    @file_path.setter
    def file_path(self):
        import warnings
        warnings.warn(
            "File Path is READ ONLY Property"
        )

    def create_path(self, user_id: int, guild_id: int) -> str:
        bf = self.file_path
        return f"{bf}/guild_{guild_id}/user_{user_id}"

    async def send_with_webhook(self, *args, **kwargs):
        # maybe its crash everything, but i dk
        session = aiohttp.ClientSession()
        webhook = Webhook.from_url(
            self.data['bot']['onreadyurl'],
            adapter=AsyncWebhookAdapter(
                session))
        await webhook.send(*args, **kwargs)
        await session.close()

    async def wait_until_r(self):
        await self.wait_until_ready()

    async def run_bot(self):
        # extensions for setup in bot
        self.extensions_ = [
            "admin", "edit", "misc", "owner",
            "visual", "write", "events",
        ]

        for extension in self.extensions_:
            try:
                self.load_extension(f"app.cogs.{extension}")
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

        logger.info("BOT READY")
        await self.wait_until_r()

        # await self.send_with_webhook(random.choice(random_text))

    async def create_error_letter(self, error, ctx):
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
