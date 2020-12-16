from discord.ext import commands
from discord.ext.commands import errors
import discord
from loguru import logger

from data.config import dstr

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
    async def on_command(self, ctx: commands.Context):
        if not ctx.guild:
            logger.info(f"Activated command {ctx.command.name}, user: {ctx.author.name}")
        logger.info(f"Activated command {ctx.command.name}, user: {ctx.author.name}, guild: {ctx.guild.name}")

def setup(bot):
    bot.add_cog(DiscordEvents(bot))