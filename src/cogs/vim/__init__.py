from discord.ext import commands
import discord

from .utils.urlcheck import UrlCheck

_ = i18n.getext

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
    async def go_to_line(self, ctx: commands.Context, *, line: str):
        if not line.isdigit():
            return

        # here goto to line file

    @commands.command()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        pass

    @commands.command()
    async def problems(self, ctx: commands.Context):
        pass

    @commands.command()
    async def remove_line(self, ctx: commands.Context, *, line: str):
        if not line.isdigit():


    @commands.command()
    async def load_file(self, ctx: commands.Context):
        check_url = UrlCheck(ctx.message.content)
        check = check_url.check()

        if check is False:
            return await ctx.send(_("Dont try load other file, we only load from cdn.discord.com"))

