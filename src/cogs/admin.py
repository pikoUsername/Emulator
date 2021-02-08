from discord.ext import commands
import discord

from ..models import User, reg_user


class AdminCommands(commands.Cog, name="Admin"):
    __slots__ = "bot",
    """ Here Admin commands, and mod commands """

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(AdminCommands(bot))
