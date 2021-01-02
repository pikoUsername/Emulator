from discord.ext import commands
import discord
from loguru import logger

from src.models import Guild, GuildAPI, UserApi
from ..utils.notify import notify_all_owners


class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("BOT READY!")
        await notify_all_owners(self.bot, text="BOT_STARTED")

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
