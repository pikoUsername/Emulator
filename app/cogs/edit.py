from discord.ext import commands

from .utils import CustomContext


class Edit(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def edit_l(self, ctx: CustomContext, line: int, *, w_text: str):
        """Edit Selected Line"""
        pass


def setup(bot):
    bot.add_cog(Edit(bot))
