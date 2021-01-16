from discord.ext import commands

from .utils import set_owner


class Owner(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx) -> bool:
        async with self.bot.bind.acquire() as connection:
            async with connection.transaction():
                is_owner = await connection.fetch("""
                    SELECT is_owner FROM users
                    WHERE user_id = $1 LIMIT 1;
                """, ctx.author.id)
                if is_owner is False:
                    return False
                return True

    @commands.command(aliases="add_owner")
    async def add_owner(self, ctx: commands.Context, user_id: int, remove: str = "1"):
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