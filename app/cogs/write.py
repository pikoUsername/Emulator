from discord.ext import commands


class Write(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['w'])
    async def write(self, ctx, *, txt: str):
        """Write To Cursor Position"""
        pass


def setup(bot):
    bot.add_cog(Write(bot))
