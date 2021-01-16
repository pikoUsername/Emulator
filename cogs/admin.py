from discord.ext import commands


class Admin(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def del_user(self, ctx: commands.Context, user_id: int):
        """Del Selected User, only for Admins"""
        pass


def setup(bot):
    bot.add_cog(Admin(bot))
