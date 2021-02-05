from discord.ext import commands


class Admin(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Admin(bot))
