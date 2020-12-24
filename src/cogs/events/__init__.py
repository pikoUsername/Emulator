from discord.ext import commands
import discord
from loguru import logger

from src.db import GuildAPI
from data.base_cfg import dint

class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_channel: discord.TextChannel = dint("START_CHANNEL", None)
        self.error_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.start_channel.send("BOT STARTED")
        except Exception:
            pass
        logger.info("BOT READY!")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

    @commands.Cog.listener()
    async def on_message_edit(self, after, before):
        """ Handler for edited messages, re-executes commands """
        if before.content != after.content:
            await self.on_message(after)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guild = await GuildAPI.get_guild(guild.id)

        if not guild:
            gapi = GuildAPI()
            await gapi.add_guild(guild)


def setup(bot):
    bot.add_cog(DiscordEvents(bot))