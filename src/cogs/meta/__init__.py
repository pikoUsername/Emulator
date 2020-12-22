from discord.ext import commands
import discord

class MetaCommands(commands.Cog):
    """ Trash Commands """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def hello(self, ctx: commands.Context):
        return await ctx.send(f"Hello i m {discord.User.mention}")

def setup(bot):
    bot.add_cog(MetaCommands(bot))
