from discord.ext import commands
from loguru import logger

from .utils.urlcheck import UrlCheck
from src.db.user import UserApi
from src.db.guild import GuildAPI
from src.utils.file_manager import FileManager
from data.config import dstr

class TextRedacotorCog(commands.Cog):
    def __init__(self, bot):
        self.bot: 'Bot' = bot
        self.userapi = UserApi()

    @commands.command()
    @commands.guild_only()
    async def start(self, ctx: commands.Context):
        user = await UserApi.get_user_by_id(user_id=ctx.author.id)
        guild = await GuildAPI.get_guild(ctx.guild.id)

        if not user:
            try:
                await UserApi.add_new_user(user=ctx.author, guild=ctx.guild)
                await ctx.send("You was logged in, and you have a folder!")

                user_ = await UserApi.get_user_by_id(ctx.author.id)
                fm =    FileManager(self.bot.loop)

                if not guild:
                    return await fm.create_user_folder(user_)
                await fm.create_user_folder(user=user_)
            except Exception as e:
                logger.exception(e)
                return await ctx.send("ERROR in creating folder and main.py script!")
        await ctx.send("Succes created folder with ur name!")

    @commands.command()
    async def add(self, ctx: commands.Context, *, text):
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            await ctx.send(f"You must be a registrated as a user, type {dstr('PREFIX')}start")
            return



    @commands.command()
    async def delete(self, ctx: commands.Context, **kwargs):
        pass

    @commands.command()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        pass


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
        pass # here creating folder(only owner)

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
