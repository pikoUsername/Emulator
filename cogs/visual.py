from discord.ext import commands


class Visual(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def all(self, ctx: commands.Context):
        """Show All File."""
        pass

    @commands.command(aliases="o")
    async def open(self, ctx: commands.Context, file: str):
        """Show Selected File."""
        pass

    @commands.command()
    async def line(self, ctx: commands.Context, line: int):
        """Show Selected Line, In Current File"""
        pass


def setup(bot):
    bot.add_cog(Visual(bot))