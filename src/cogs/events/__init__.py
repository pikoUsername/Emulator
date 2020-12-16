from discord.ext import commands
import discord
from loguru import logger

from src.db import GuildAPI

class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("BOT READY!")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        logger.info("<User name={0.author.name}, id={0.id}, content={0.content}>".format(msg))

    @commands.Cog.listener()
    async def on_message_edit(self, after, before):
        """ Handler for edited messages, re-executes commands """
        if before.content != after.content:
            await self.on_message(after)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        try:
            logger.info(f"Activated command {ctx.command.name}, user: {ctx.author.name}, guild: {ctx.guild.name}")
        except Exception:
            logger.info(f"Activated command {ctx.command.name}, user: {ctx.author.name}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guild = await GuildAPI.get_guild(guild.id)

        if not guild:
            gapi = GuildAPI()
            await gapi.add_guild(guild)
        # fm = FileManager(self.bot.loop)
        # await fm.create_guild_folder(guild)

def setup(bot):
    bot.add_cog(DiscordEvents(bot))