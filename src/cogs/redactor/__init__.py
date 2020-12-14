from discord.ext import commands
import discord

from .utils.delete import DeleteCheck
from .utils.urlcheck import UrlCheck

class TextRedacotorCog(commands.Cog):
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
    async def change_line(self, ctx: commands.Context, *, text: str):
        if len(text) <= 200:
            await ctx.send("Limit 200 letters")
            return

    @commands.command()
    async def remove_line(self, ctx: commands.Context, *, line: str):
        if not line.isdigit():
            await ctx.send("Not correct line!")
            return

        # here removing line(run in executor)

    @commands.command()
    async def load_file(self, ctx: commands.Context, *, file: str):
        check_url = UrlCheck(ctx.message.content)
        check = check_url.check()

        if check is False:
            return await ctx.send("Dont try load other file, we only load from cdn.discord.com")

    @commands.command()
    async def upload_file(self, ctx: commands.Context, *, filename: str):
        pass

    @commands.command()
    async def rm_file(self, ctx: commands.Context, *, files: str):
        for file in files:
            pass # here deleting files!

    @commands.command()
    @commands.is_owner()
    async def mkdir(self, ctx: commands.Context, *, name: str):
        pass # here creating file(only owner)

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
