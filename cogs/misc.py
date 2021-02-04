from discord.ext import commands


class Misc(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["q"])
    async def quit(self, ctx: commands.Context):
        pass

    @commands.command(aliases=["s/"])
    async def search(self, ctx: commands.Context, *, args: str):
        pass

    @commands.command()
    async def start(self, ctx: commands.Context, ref_id: int):
        """
        On Type command, check out if user exists,
        and if user exists, then he ll send the fuck
        Usage
        ```

        """
        pass

def setup(bot):
    bot.add_cog(Misc(bot))
