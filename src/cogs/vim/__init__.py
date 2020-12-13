from discord.ext import commands
import discord

class VimCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx: commands.Context, *, kwargs):
        pass

    @commands.command()
    async def delete(self, ctx: commands.Context, **kwargs):
        pass

    @commands.command()
    async def go_to(self, ctx: commands.Context, *, line: str):
        if not line.isdigit():
            return

        # here goto to file

    @commands.command()
    async def problems(self, ctx: commands.Context):
