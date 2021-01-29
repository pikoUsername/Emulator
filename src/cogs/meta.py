from typing import Union
import time

import asyncpg
from discord.ext import commands
import discord

from ..models import User
from ..utils.set_owner import create_owner_user
from ..utils.help import PaginatedHelpCommand
from ..config import POSTGRES_URI


class MetaCommands(commands.Cog, name="Meta"):
    __slots__ = ("bot", "old_help_command")
    """Utils Commands, And Some Fun..."""
    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    @commands.command(hidden=True)
    async def hello(self, ctx: commands.Context):
        return await ctx.send(
            "Hello, Здравствуйте, Здрастуйте, Hallo, 여보세요, dzień dobry, Bonjour, こんにちは, Сәлеметсіз бе")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def get_owner(self,
                        ctx: commands.Context,
                        member: Union[discord.Member, discord.User] = None):
        user_id = member.id if member else ctx.author.id
        user = await User.get_user_by_id(user_id)

        try:
            result = await create_owner_user(user.user_id, remove=False)
        except ValueError:
            result = None

        if not result:
            return await ctx.send("Failed To Create Admin User, User not exists")
        return await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.is_owner()
    async def execute(self, ctx: commands.Context, *, sql: str):
        async with asyncpg.create_pool(POSTGRES_URI) as pool:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.excute(sql)
        return ctx.send("Successfully completed execute opration")

    @commands.command()
    @commands.is_owner()
    async def fetch(self, ctx: commands.Context, *, sql: str):
        f_time = time.time()
        with asyncpg.create_pool(POSTGRES_URI) as pool:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    if '$' in sql:
                        return await ctx.send("in sql cant be a $1 argument")
                    result = await conn.fetch(sql)
                    if len(result) >= 4028:
                        return await ctx.send("SQL result more than 4028 letters")

        s_time = time.time() - f_time
        await ctx.send("\n".join(result) if result else "Nothing ...")
        await ctx.send(f"Completed in ``{s_time}``")

def setup(bot):
    bot.add_cog(MetaCommands(bot))
