from typing import Union

from discord.ext import commands
import discord

from src.models import UserApi
from src.utils.set_owner import create_owner_user
from src.utils.help import PaginatedHelpCommand


class MetaCommands(commands.Cog):
    __slots__ = "bot",
    """ Trash Commands """
    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    @commands.command(hidden=True)
    async def hello(self, ctx: commands.Context):
        return await ctx.send(f"Hello, Здравствуйте, Здрастуйте, Hallo, 여보세요, dzień dobry, Bonjour, こんにちは, Сәлеметсіз бе")

    @commands.command()
    async def no(self, ctx: commands.Context):
        return await ctx.send(">> yes")

    @commands.command()
    async def yes(self, ctx: commands.Context):
        return await ctx.send(">> no")

    @commands.command()
    @commands.is_owner()
    async def get_owner(self, ctx: commands.Context, member: Union[discord.Member, discord.User]=None):
        user_id = member.id or ctx.author.id
        user = await UserApi.get_user_by_id(user_id)

        try:
            result = await create_owner_user(user.user_id, remove=False)
        except ValueError:
            result = None

        if not result:
            return await ctx.send("Failed To Create Admin User, User not exists")
        return await ctx.message.add_reaction("✅")


def setup(bot):
    bot.add_cog(MetaCommands(bot))
