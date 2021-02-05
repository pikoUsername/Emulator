from discord.ext import commands
from loguru import logger

from app.cogs.utils import CustomContext


class Events(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            return
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CustomContext, err):
        missing_perms = (
            commands.BotMissingPermissions,
            commands.MissingPermissions
        )
        ignore_errors = (
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.TooManyArguments,
            commands.BadUnionArgument
        )
        if isinstance(err, ignore_errors):
            await ctx.send_help(ctx.command)

        elif isinstance(err, missing_perms):
            await ctx.send("**M**issing **R**equired **P**ermissions")
        elif isinstance(err, commands.CommandNotFound):
            pass
        else:
            logger.error(err)
            await self.bot.create_error_letter(err, ctx)


def setup(bot):
    bot.add_cog(Events(bot))
