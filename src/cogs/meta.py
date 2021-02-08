import time

from discord.ext import commands

from ..utils.help import PaginatedHelpCommand


class MetaCommands(commands.Cog, name="Meta"):
    __slots__ = ("bot", "old_help_command")
    """Utils Commands, And Some Fun..."""
    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    @commands.command()
    async def test(self, ctx):
        ftime = time.time()
        message = await ctx.send("Test...")
        await message.delete()
        await ctx.send(time.time() - ftime)


def setup(bot):
    bot.add_cog(MetaCommands(bot))
