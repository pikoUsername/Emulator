from discord.ext import commands
from loguru import logger
import discord

from src.utils.http import post, get
from .utils.urlcheck import UrlCheck
from src.db.user import UserApi, User
from src.utils.file_manager import FileManager
from src.db.guild import GuildAPI
from data.config import dstr

class TextRedacotorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userapi = UserApi()
        self.fm: FileManager = self.bot.fm

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
                fm = self.fm

                if not guild:
                    return await fm.create_user_folder(user_)
                await fm.create_user_folder(user=user_)
            except Exception as e:
                logger.exception(e)
                return await ctx.send("ERROR in creating folder and main.py script!")
        await ctx.send(embed=discord.Embed(title=f"Succes {self.bot.APPLY_EMOJI}", description="Succes created folder with ur name!"))

    @commands.command()
    async def add(self, ctx: commands.Context, *, text: str):
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            await ctx.send(f"You must be a registered as a user, type {dstr('PREFIX')}start")
            return

    @commands.command()
    async def delete(self, ctx: commands.Context, **kwargs):
        pass

    @commands.command()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        pass


    @commands.command(aliases=["remove_line"])
    async def rm_line(self, ctx: commands.Context, *, line: str):
        """
remove selected line, if you was wrong write ctrl-z
        """
        if not line.isdigit():
            await ctx.send("Not correct line!")
            return

        user = self.bot.uapi.get_user_by_id(ctx.author.id)

        await self.bot.fm.remove_line(line, user)
        # here removing line(run in executor)

    @commands.command()
    async def upload_file(self, ctx: commands.Context, *, filename: str):
        pass

    @commands.command()
    async def rm_file(self, ctx: commands.Context, *, file: str):
        """
remove selected file, be cary about it!
        """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start, and comehere there")
        await self.fm.remove_file(file, user)


    @commands.command()
    @commands.is_owner()
    async def mkdir(self, ctx: commands.Context, path: str, *, name: str):
        """
make dir in any directory! only owner
        """
        pass # here creating folder(only for owner)

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
