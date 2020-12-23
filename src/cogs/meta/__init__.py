from discord.ext import commands
import discord

class MetaCommands(commands.Cog):
    """ Trash Commands """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def hello(self, ctx: commands.Context):
        return await ctx.send(f"Hello, Здравствуйте, Здрастуйте, Hallo, 여보세요, dzień dobry, Bonjour, こんにちは, Сәлеметсіз бе")

    @commands.command(hidden=True)
    async def no(self, ctx: commands.Context):
        return await ctx.send(">> yes")

    @commands.command(hidden=True)
    async def yes(self, ctx: commands.Context):
        return await ctx.send(">> no")

def setup(bot):
    bot.add_cog(MetaCommands(bot))
