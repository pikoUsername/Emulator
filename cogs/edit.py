from discord.ext import commands
import discord


class Edit(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def edit_l(self, ctx: commands.Context, *, wtext: str):
        pass


def setup(bot):
    bot.add_cog(Edit(bot))