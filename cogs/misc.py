from discord.ext import commands


class Misc(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["q"])
    async def quit(self, ctx: commands.Context):
        pass

    @commands.command(aliases="s/")
    async def search(self, ctx: commands.Context):
        pass

    @commands.command(aliases="undo")
    async def undo(self, ctx: commands.Context):
        pass


def setup(bot):
    bot.add_cog(Misc(bot))