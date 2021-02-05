from discord.ext import commands

from app.cogs.utils import CustomContext


class Write(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['w'])
    async def write(self, ctx: CustomContext, *, txt: str):
        """Write To Cursor Position"""
        pass


def setup(bot):
    bot.add_cog(Write(bot))
