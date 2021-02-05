from discord.ext import commands

from .utils import set_owner, CustomContext


class Owner(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    # async def cog_check(self, ctx: CustomContext) -> bool:
    #     sql = "SELECT is_owner FROM users WHERE user_id = $1;"
    #     is_owner = await ctx._make_request(sql, (ctx.author.id,), fetch=True)
    #     return bool(is_owner)

    @commands.command()
    async def add_owner(self, ctx: CustomContext, user_id: int, remove: str = "1"):
        """Add Owner by id"""
        r = int(remove) if remove.isdigit() else None

        if r is None:
            return await ctx.send("Remove argument Is Not Digit")

        try:
            result = await set_owner(user_id, bool(r))
        except TypeError:
            result = False

        if not result:
            return await ctx.send("User Not Exists")
        return await ctx.send("Owner User Successfully Created")


def setup(bot):
    bot.add_cog(Owner(bot))
