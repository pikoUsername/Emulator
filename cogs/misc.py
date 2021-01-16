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
        user = await self.bot.dbc.get_user(ctx.author.id)
        if user:
            return await ctx.send("You Aleardy in db")

        await self.bot.dbc.add_new_user(ctx.author)


def setup(bot):
    bot.add_cog(Misc(bot))
