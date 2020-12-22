import os

from discord.ext import commands
from loguru import logger
import discord

from .utils.urlcheck import UrlCheck
from src.utils.file_manager import FileManager
from src.db import GuildAPI, UserApi
from data.base_cfg import dstr
from data.base_cfg import BASE_PATH

class TextRedacotorCog(commands.Cog):
    """ typical file redactor """
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
        """ add current file text which you add in command """
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            await ctx.send(f"You must be a registered as a user, type {dstr('PREFIX')}start")
            return

    @commands.command()
    @commands.guild_only()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        """
        Set current file, and checks you out
        If you exists, your talbe current_file changes
        """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start for start")
        if not os.path.exists(f"{user.user_path}/{file}"):
            return await ctx.send("File not exists")

        await user.update(current_file=f"{user.user_path}/{file}").apply()
        await ctx.send(embed=discord.Embed(title=f"Succes, {self.bot.APPLY_EMOJI}", description=f"Now your current file is ``{file}``"))

    @commands.command(aliases=["remove_line"])
    @commands.guild_only()
    async def rm_line(self, ctx: commands.Context, *, line: str):
        """ remove selected line in currect file, make sure you know what there"""
        if not line.isdigit():
            await ctx.send("perametr not a digit!")
            return
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed()

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)

        embed = discord.Embed()
        try:
            embed.title = f"Succes deleted line, {self.bot.APPLY_EMOJI}"
            embed.description = f"Deleted line {line}"

            await self.bot.fm.change_line(user, line)
        except Exception:
            embed.title = f"Error to remove line {self.bot.X_EMOJI}"
            embed.description = "Error to remove line,\n failed, we track automacly error,\n but if error left then write bug report"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def write(self, ctx: commands.Context, file_: str,  *, text: str):
        """ Check choosed file, you can type anything """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed()

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)

        user_file = f"{user.user_path}\{file_}"
        embed = discord.Embed()

        try:
            with open(user_file, "w") as file:
                await self.bot.loop.run_in_executor(None, file.write, text)
            embed.title = f"Succes, {self.bot.APPLY_EMOJI}"
            embed.description = f"Writed to {file_}."
        except FileNotFoundError:
            embed.title = f"ERROR, {self.bot.X_EMOJI}"
            embed.description = "Error, file not exists"
        except UnicodeEncodeError:
            embed.title = f"ERROR {self.bot.X_EMOJI}"
            embed.description = "You try write to file, emoji or something like this, its unacceptable"
        return await ctx.send(embed=embed)

    @commands.command(aliases=["current_file"])
    @commands.guild_only()
    async def cf(self, ctx: commands.Context):
        """ get current user file """
        user = await self.userapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed()

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)

        return await ctx.send(f"Your current file ```{user.current_file}```")
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

    @commands.command(aliases=["create_file"])
    @commands.guild_only()
    async def touch(self, ctx: commands.Context, name: str, *, type_: str="py"):
        """ create file in your folder """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed()

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)


        if len(name) >= 300:
            return await ctx.send(embed=discord.Embed(
                title=f"Not have enough access {self.bot.X_EMOJI}",
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
    async def ls(self, ctx: commands.Context, *, member: discord.Member=None):
        """ List files """
        if not member:
            user = await self.userapi.get_user_by_id(ctx.author.id)
        else:
            user = await self.userapi.get_user_by_id(member.id)

        if not user:
            embed = discord.Embed()

            embed.title = "User didnt authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)
        all_files = await self.bot.loop.run_in_executor(None, os.listdir, user.user_path)

        await ctx.send(embed=discord.Embed(
            title=f"All files in your directory",
            description="\n".join(all_files),
        ))

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
