from discord.ext import commands
import discord
from loguru import logger

from src.models import Guild, GuildAPI

class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            start_channel = getattr(self.bot, 'start_channel', None)
            await start_channel.send("BOT STARTED")
        except TypeError:
            pass
        logger.info("BOT READY!")

    @commands.Cog.listener()
    async def on_message_edit(self, after, before):
        """ Handler for edited messages, re-executes commands """
        if before.content != after.content:
            await self.bot.on_message(after)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guild = await Guild.query.where(guild.id == Guild.guild_id).gino.first()

        if not guild:
            gapi = GuildAPI()
            await gapi.add_guild(guild)


def setup(bot):
    bot.add_cog(DiscordEvents(bot))
