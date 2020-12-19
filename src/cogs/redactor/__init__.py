import os

from discord.ext import commands
from loguru import logger
import discord

from .utils.urlcheck import UrlCheck
from src.utils.file_manager import FileManager
from src.db import GuildAPI, UserApi
from data.config import dstr
from data.base_cfg import BASE_PATH

class TextRedacotorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userapi = UserApi()
        self.fm: FileManager = self.bot.fm

    @commands.command()
    @commands.guild_only()
    async def start(self, ctx: commands.Context):
        """ register user, and create user folder in guild"""
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
                await fm.create_file(file_name="main", user=user_)
            except Exception as e:
                logger.exception(e)
                return await ctx.send("ERROR in creating folder and main.py script!")
        await ctx.send(embed=discord.Embed(title=f"Success {self.bot.APPLY_EMOJI}", description="Succes created folder with ur name!"))

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
        """ Set current file """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"/shrug Type {self.bot.command_prefix}start for start")
        if not os.path.exists(f"{user.user_path}/{file}"):
            return await ctx.send("File not exists")

        await user.update(current_file=f"{user.user_path}/{file}")
        await ctx.send(embed=discord.Embed(title="Go to File", description=f"Now your current file {file}"))

    @commands.command(aliases=["remove_line"])
    @commands.guild_only()
    async def rm_line(self, ctx: commands.Context, *, line: str):
        """ remove selected line in currect file"""
        if not line.isdigit():
            await ctx.send("Not correct line!")
            return

        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        await self.bot.fm.remove_line(line, user)

    @commands.command()
    @commands.guild_only()
    async def current_file(self, ctx: commands.Context):
        """ get current user file """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start to start")
        return await ctx.send(f"Your current file ```{user.current_file}```")

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
            await ctx.send("Success you created folder")
        except Exception as e:
            await ctx.send("Failed creating folder!")
            await self.bot.error_channel.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(3, 4000)
    async def create_file(self, ctx: commands.Context, name: str, *, type_: str="py"):
        """ create file in your folder """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(embed=discord.Embed(title=f"User not authed {self.bot.X_EMOJI}",
                                                              description=f"Type {self.bot.command_prefix}start for use this command"))

        if len(name) >= 300:
            return await ctx.send(embed=discord.Embed(
                title=f"{self.bot.X_EMOJI}",
                description="Too long file name",
            ))
        elif os.path.exists(f"{BASE_PATH}/{name}.{type_}"):
            await ctx.send("this File aleardy exists")

        await ctx.send("Creating File...")

        try:
            await self.fm.create_file(name, user, type_)
        except Exception as e:
            logger.exception(e)
            return await ctx.send(embed=discord.Embed(
                title=f"ERROR, {self.bot.X_EMOJI}",
                description=f"```{e}```",
            ))
        else:
            await ctx.send(embed=discord.Embed(title=f"Succes! {self.bot.APPLY_EMOJI}",description=f"Created file {name}"))

    @commands.command(aliases=["list", "list_files"])
    @commands.guild_only()
    async def ls(self, ctx: commands.Context):
        """ List files """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start to start")
        all_files = await self.bot.loop.run_in_executor(None, os.listdir, user.user_path)

        await ctx.send(embed=discord.Embed(
            title=f"All files in your directory",
            description="\n".join(all_files),
        ))

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
