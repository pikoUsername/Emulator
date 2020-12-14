from discord.ext import commands
import discord
from loguru import logger

class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("BOT READY!")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        logger.info("<User name={0.author.name}, id={0.id}, content={0.content}>".format(msg))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, commands.NoPrivateMessage):
            pass
        elif isinstance(exc, commands.BadArgument or commands.BadUnionArgument):
            await ctx.send("Wrong argmuments of command")
        elif isinstance(exc, commands.CommandInvokeError):
            logger.exception(exc)
            await ctx.send("Command Not found or Crashed")
        else:
            logger.exception(exc)

def setup(bot):
    bot.add_cog(DiscordEvents(bot))