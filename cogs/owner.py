from discord.ext import commands


class Owner(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx) -> bool:
        async with self.bot.bind.acquire() as connection:
            async with connection.transaction():
                is_admin = await connection.fetch("""
                    SELECT is_admin FROM users
                    WHERE user_id = $1 LIMIT 1;
                """, ctx.author.id)
                if is_admin is False:
                    return False
                return True

    @commands.command(aliases="add_owner")
    async def add_owner(self, ctx: commands.Context, user_id: int, remove: int):
        """Add Owner by id"""
        pass


def setup(bot):
    bot.add_cog(Owner(bot))