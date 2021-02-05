from discord.ext import commands


class Visual(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def all(self, ctx):
        """Show whole File."""
        pass

    @commands.command(aliases=["o"])
    async def open(self, ctx, file: str):
        """Show Selected File."""
        pass

    @commands.command()
    async def line(self, ctx, line: int):
        """Show Selected Line, In Current File"""
        pass


def setup(bot):
    bot.add_cog(Visual(bot))
