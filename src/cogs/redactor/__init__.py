import asyncio
import os

from discord.ext import commands
from loguru import logger
import discord

from src.utils.http import post, get
from .utils.urlcheck import UrlCheck
from src.db.user import UserApi
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
        """ register author user, and create user folder in guild, work only in guild """
        user = await UserApi.get_user_by_id(user_id=ctx.author.id)
        guild = await GuildAPI.get_guild(ctx.guild.id)

        if user:
            return await ctx.send(embed=discord.Embed(
                title=f"Access Error {self.bot.X_EMOJI}",
                description="You aleardy registered in DB!",
            ))

        if not user:
            try:
                await UserApi.add_new_user(user=ctx.author, guild=ctx.guild)

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
    @commands.guild_only()
    async def add(self, ctx: commands.Context, *, text: str):
        """ re-write choosed file! """
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            await ctx.send(f"You must be a registered as a user, type {dstr('PREFIX')}start")
            return

    @commands.command()
    @commands.guild_only()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        pass


    @commands.command(aliases=["remove_line"])
    @commands.guild_only()
    async def rm_line(self, ctx: commands.Context, *, line: str):
        """ remove selected line, if you was wrong write ctrl-z """
        if not line.isdigit():
            await ctx.send("Not correct line!")
            return

        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        await self.bot.fm.remove_line(line, user)


    @commands.command()
    @commands.guild_only()
    async def upload_file(self, ctx: commands.Context, *, filename: str):
        pass

    """ not working yet, danger 
    @commands.command()
    async def rm_file(self, ctx: commands.Context, *, file: str):
        remove selected file, be cary about it!
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start, and comehere there")
        await self.fm.remove_file(file, user)
    """


    @commands.command()
    @commands.is_owner()
    async def mkdir(self, ctx: commands.Context, path: str, *, name: str):
        """ make dir in any directory! only owner """
        loop = self.bot.loop

        to_create = f"{path}/{name}"
        try:
            await loop.run_in_executor(None, os.mkdir, to_create)
            await ctx.send("Success you created folder ")
        except Exception as e:
            await ctx.send("Failed to creating folder!")
            await self.bot.error_channel.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(3, 4000)
    async def create_file(self, ctx: commands.Context, *, name: str, type: str="py"):
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(embed=discord.Embed(title=f"User not authed {self.bot.X_EMOJI}",
                                                              description=f"Type {self.bot.command_prefix}start for use this command"))

        if len(name) >= 300:
            return await ctx.send(embed=discord.Embed(
                title=f"{self.bot.X_EMOJI}",
                description="Too long file name",
            ))

        await ctx.send("Creating File...")

        try:
            await self.fm.create_file(name, user, type)
        except Exception as e:
            logger.exception(e)
            return await ctx.send(embed=discord.Embed(
                title=f"ERROR, {self.bot.X_EMOJI}",
                description=f"```{e}```",
            ))
        else:
            await ctx.send(embed=discord.Embed(title=f"Succes! {self.bot.APPLY_EMOJI}",description=f"Created file {name}"))


def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
