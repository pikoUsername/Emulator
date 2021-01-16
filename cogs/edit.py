from discord.ext import commands


class Edit(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def edit_l(self, ctx: commands.Context, *, w_text: str):
        """Edit Current Line"""
        pass


def setup(bot):
    bot.add_cog(Edit(bot))
