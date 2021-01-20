import asyncio
import argparse
import os
from os.path import join
import time

from discord.ext import commands
from loguru import logger
import discord

from src.utils.file_manager import FileManager
from src.models import GuildAPI, UserApi
from .utils.upload import load_code_from_github
from src.config import BASE_PATH


class TextRedacotorCog(commands.Cog):
    __slots__ = "bot", "fm"
    """ typical file redactor """
    def __init__(self, bot):
        self.bot = bot
        self.fm: FileManager = self.bot.fm

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command cannot be used in private messages.')
        return True

    @commands.command()
    async def upload_from_github(self, ctx: commands.Context, owner: str, repo: str, branch: str = "master"):
        """
        Create Repo In Your User Directory, And Its Not Working.
        """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        try:
            await load_code_from_github(owner, repo, user, branch)
        except AttributeError:
            return await ctx.send(f"Type {self.bot.command_prefix}start for start")

    @commands.command()
    async def start(self, ctx: commands.Context):
        """ register user, and create user folder in guild"""
        user = await UserApi.get_user_by_id(user_id=ctx.author.id)
        if user:
            return await ctx.send(embed=discord.Embed(
                title=f"Access Error {self.bot.X_EMOJI}",
                description="You aleardy registered in DB!",
                colour=discord.Colour.red(),
            ))
        if not user:
            try:
                user = await UserApi.add_new_user(ctx.author, ctx.guild)
                guild = await GuildAPI.get_guild(ctx.guild.id)

                if not guild:
                    return await self.fm.create_user_folder(user)
                await self.fm.create_user_folder(user=user)
                await self.fm.create_file(file_name="main", user=user)
            except Exception as e:
                logger.exception(e)
                return await ctx.send("ERROR in creating folder and main.py script!")
        await ctx.send(embed=discord.Embed(title=f"Success {self.bot.APPLY_EMOJI}",
                                           description="Success created folder with ur name!",
                                           colour=discord.Colour.blue()))

    @commands.command()
    async def add(self, ctx: commands.Context, *, text: str):
        """ add current file text which you add in command """
        user = await UserApi.get_user_by_id(ctx.author.id)
        try:
            await self.fm.write_to_file(text, user)
            await ctx.message.add_reaction("✅")
        except AttributeError:
            await ctx.send(f"You must be a registered as a user, type {self.bot.command_prefix}start")

    @commands.command()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        """
        Set current file, and checks you out
        If you exists, your talbe current_file changes
        """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        if not os.path.exists(f"{user.user_path}/{file}"):
            return await ctx.send("File not exists")

        try:
            await user.update(current_file=f"{user.user_path}/{file}").apply()
        except AttributeError:
            return await ctx.send(f"Type {self.bot.command_prefix}start for start")
        await ctx.send(embed=discord.Embed(title=f"Success, {self.bot.APPLY_EMOJI}",
                                           description=f"Now your current file is ``{file}``"))

    @commands.command(aliases=["remove_line"])
    async def rm_line(self, ctx: commands.Context, *, line: str):
        """ remove selected line in currect file, make sure you know what there"""
        if not line.isdigit():
            await ctx.send("perameter not a digit!")
            return
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        embed = discord.Embed()
        try:
            embed.title = f"Success deleted line, {self.bot.APPLY_EMOJI}"
            embed.description = f"Deleted line {line}"

            await self.bot.fm.change_line(user, line)
        except AttributeError:
            return await ctx.send(f"Type {self.bot.command_prefix}start for start")
        await ctx.send(embed=embed)

    @commands.command(aliases=("mv",))
    async def move(self, ctx: commands.Context, file: str, *, to_change: str):
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        try:
            result = await self.fm.change_file_name(user, file, to_change)
        except (FileNotFoundError, PermissionError) as e:
            logger.error(e)
            result = None
        except AttributeError:
            return await ctx.send("You not Authed")

        if not result:
            return await ctx.send("Failed To Change Name File")
        return await ctx.message.add_reaction("✅")

    @commands.command(alises=("w",))
    async def write(self, ctx: commands.Context, file: str, *, text: str):
        """ Write to current file, if you do not select file. You can type anything """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        user_file = file or user.current_file
        embed = discord.Embed(colour=discord.Colour.random())

        try:
            with os.open(user_file, os.O_RDONLY) as file:
                await self.bot.loop.run_in_executor(None, file.write, text)
            embed.title = f"Succes {self.bot.APPLY_EMOJI}"
            embed.description = f"Writed to current file, check it with command, {self.bot.command_prefix}cf."
        except FileNotFoundError:
            embed.title = f"ERROR, {self.bot.X_EMOJI}"
            embed.description = "Error, file not exists"
        except UnicodeEncodeError:
            embed.title = f"ERROR {self.bot.X_EMOJI}"
            embed.description = "You try write to file, emoji or something like this, its unacceptable"
        except AttributeError:
            return await ctx.send("You Not Authed as User")
        return await ctx.send(embed=embed)

    @commands.command(aliases=("cf",))
    async def current_file(self, ctx: commands.Context):
        """ get current user file """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        try:
            return await ctx.send(f"Your current file ```{user.current_file}```")
        except AttributeError:
            return await ctx.send("You Nor Authed as User")

    @commands.command(aliases=("rm", "remove_file", "remove"))
    async def rm_file(self, ctx: commands.Context, file: str):
        """
        remove selected file, be cary about it!

        You can select more 1 file, example:
        ```
        >> rm_file lol.py
        ```
        but cary about it, because it can be deleted forever
        """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        try:
            await ctx.message.add_reaction("✅")
        except AttributeError:
            return await ctx.send(f"Type {self.bot.command_prefix}start, and come here again")

        try:
            await self.fm.remove_file(file, user)
            await ctx.message.add_reaction("✅")
        except AttributeError:
            await ctx.message.add_reaction("❌")
        except FileNotFoundError:
            await ctx.send("File Not Exists")

    @commands.command()
    async def mkdir(self, ctx: commands.Context, path: str, *, name: str):
        """ make dir in any directory! only owner """
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user.is_owner:
            raise commands.MissingPermissions("Missing Owner permissions")
        loop = self.bot.loop

        to_create = f"{path}/{name}"
        await loop.run_in_executor(None, os.mkdir, to_create)
        await ctx.message.add_reaction("✅")
        try:
            if not user.is_owner:
                raise commands.MissingPermissions("Missing Owner permissions")
            loop = asyncio.get_event_loop()

            to_create = f"{path}/{name}"
            await loop.run_in_executor(None, os.mkdir, to_create)
            await ctx.message.add_reaction("✅")
        except AttributeError:
            return await ctx.send("You not authed as User, type command 'start'")

    @commands.command(aliases=["create_file"])
    @commands.cooldown(10, 200, commands.BucketType.channel)
    async def touch(self, ctx: commands.Context, name: str, *, type_: str = "py"):
        """ create file in your folder """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        try:
            if len(name) >= 78:
                if user.is_owner:
                    pass
                else:
                    return await ctx.send(embed=discord.Embed(
                        title=f"Not have enough access {self.bot.X_EMOJI}",
                        description="Too long file name",
                        colour=discord.Colour.blue(),
                    ))
            elif os.path.exists(f"{BASE_PATH}/{name}.{type_}"):
                await ctx.send("this File aleardy exists")

            try:
                await self.fm.create_file(name, user, type_)
            except Exception as e:
                logger.exception(e)
                return await ctx.send(embed=discord.Embed(
                    title=f"ERROR, {self.bot.X_EMOJI}",
                    description=f"```{e}```",
                    colour=discord.Colour.blue(),
                ))
            else:
                await ctx.message.add_reaction("✅")
        except AttributeError:
            return await ctx.send("You Not Authed as User")

        try:
            await self.fm.create_file(name, user, type_)
        except Exception as e:
            logger.exception(e)
            return await ctx.send(embed=discord.Embed(
                title=f"ERROR, {self.bot.X_EMOJI}",
                description=f"```{e}```",
                colour=discord.Colour.blue(),
            ))
        else:
            await ctx.message.add_reaction("✅")

    @commands.command(aliases=["list", "list_files"])
    @commands.cooldown(30, 200, commands.BucketType.guild)
    async def ls(self, ctx: commands.Context, flags: str = None, *, member: discord.Member = None):
        """
        List files, with flags

        -A: get all files with info,
        command get sorted files,
        example:
        ```
        Files:    size:   updated_at:
        just.py   23KB   1923.12.30 12:23:30
        dod.py    12KB    1923.12.23 23:43:23
        kik.js    90KB    1923.12.29 16:22:32
        ```
        """
        user_id = ctx.author.id or member.id
        user = await self.bot.uapi.get_user_by_id(user_id)
        try:
            all_files = await self.bot.loop.run_in_executor(None, os.listdir, user.user_path)
        except AttributeError:
            return await ctx.send("You Not Authed As User")

        if not flags:
            await ctx.send(embed=discord.Embed(
                title="All files in your directory",
                description="\n".join(all_files),
                colour=discord.Colour.blue(),
            ))
            return

        if flags not in ["-A", "-a"]:
            return await ctx.send_help(ctx.command)

        embed = discord.Embed(title="All files", colour=discord.Colour.blue())
        files_sorted_by_size = sorted(
            self.get_files_info(f"{user.user_path}/"), reverse=True, key=lambda x: x[1].st_size)
        sizes = []
        updated_at = []
        name_files = []

        for file_name, file_stat in files_sorted_by_size:
            sizes.append(self.sizeof_fmt(file_stat.st_size))
            updated_at.append(self.get_date_as_string(file_stat.st_mtime))

        for file in all_files:
            name_files.append(file)

        embed.add_field(name="file name", value="\n\n".join(name_files))
        embed.add_field(name="Size", value="\n\n".join(sizes))
        embed.add_field(name="updated at", value="\n\n".join(updated_at))

        await ctx.send(embed=embed)

    @commands.command()
    async def show_file(self, ctx: commands.Context, file: str = None):
        user = await UserApi.get_user_by_id(ctx.author.id)

        f = await self.bot.fm.open_file(file, user)
        e = discord.Embed(title=f"File {file}",
                          description=f"```{f}```")
        return await ctx.send(embed=e)

    @staticmethod
    def get_files_info(dir_name):
        for root, dirs, files in os.walk(dir_name):
            for file_name in files:
                abs_file_name = join(root, file_name)

                yield abs_file_name, os.stat(abs_file_name)

    @staticmethod
    def sizeof_fmt(num):
        for x in ['bytes', 'KB', 'MB', 'GB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)

            num /= 1024.0

        return "%3.1f %s" % (num, 'TB')

    @staticmethod
    def get_date_as_string(dt):
        return time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(dt))

    @commands.command(aliases=['s/'])
    async def search(self, ctx: commands.Context, *, query: str):
        """
        Search In current File
        """
        user = await UserApi.get_user_by_id(ctx.author.id)

        result = await self.bot.fm.search_in_file(query, user.current_file)
        if not result:
            return await ctx.send(embed=discord.Embed(title="Results",
                                                      description="No Results Found..."))
        return await ctx.send(embed=discord.Embed(title="Results",
                                                  description=f"```{result}```"))

    @commands.command(aliases=['cp'])
    async def copy(self, ctx: commands.Context, *, text: commands.clean_content(fix_channel_mentions=True)):
        """
        Cp like in *nix Systems, but badder
        copy current file if --file flag not setted
        """
        user = await UserApi.get_user_by_id(ctx.author.id)

        argparse_ = argparse.ArgumentParser()
        try:
            argparse_.add_argument('--file', '-f', default=user.current_user)
        except AttributeError:
            return await ctx.send(f"You Not Authed as User, type {self.bot.command_prefix}start")

        self.bot.fm.copy_file()  # 

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
