import os
from os.path import join
import time

from discord.ext import commands
from loguru import logger
import discord

from .utils.urlcheck import UrlCheck
from src.utils.file_manager import FileManager
from src.models import GuildAPI, UserApi
from data.config import dstr, PREFIX, BASE_PATH


class TextRedacotorCog(commands.Cog):
    """ typical file redactor """
    def __init__(self, bot):
        self.bot = bot
        self.fm: FileManager = self.bot.fm

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command cannot be used in private messages.')
        return True

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

        guild = await GuildAPI.get_guild(ctx.guild.id)
        if not user:
            try:
                await UserApi.add_new_user(user=ctx.author, guild=ctx.guild)

                user_ = await UserApi.get_user_by_id(ctx.author.id)

                if not guild:
                    return await self.fm.create_user_folder(user_)
                await self.fm.create_user_folder(user=user_)
                await self.fm.create_file(file_name="main", user=user_)
            except Exception as e:
                logger.exception(e)
                return await ctx.send("ERROR in creating folder and main.py script!")
        await ctx.send(embed=discord.Embed(title=f"Success {self.bot.APPLY_EMOJI}", description="Success created folder with ur name!", colour=discord.Colour.blue()))

    @commands.command()
    async def add(self, ctx: commands.Context, *, text: str):
        """ add current file text which you add in command """
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            await ctx.send(f"You must be a registered as a user, type {dstr('PREFIX')}start")
            return
        try:
            await self.fm.write_to_file(text, user)
            await ctx.message.add_reaction("✅")
        except Exception:
            await ctx.message.add_reaction("❌")

    @commands.command()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        """
        Set current file, and checks you out
        If you exists, your talbe current_file changes
        """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start for start")
        if not os.path.exists(f"{user.user_path}/{file}"):
            return await ctx.send("File not exists")

        await user.update(current_file=f"{user.user_path}/{file}").apply()
        await ctx.send(embed=discord.Embed(title=f"Succes, {self.bot.APPLY_EMOJI}", description=f"Now your current file is ``{file}``"))

    @commands.command(aliases=["remove_line"])
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
        except commands.CommandInvokeError:
            embed.title = f"Error to remove line {self.bot.X_EMOJI}"
            embed.description = "Error to remove line,\n failed, we track automacly error,\n but if error left then write bug report"
        await ctx.send(embed=embed)

    @commands.command(aliases=("mv",))
    async def move(self, ctx: commands.Context, file: str, *, to_change: str):
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        try:
            result = await self.fm.change_file_name(user, file, to_change)
        except (FileNotFoundError, PermissionError) as e:
            logger.error(e)
            result = None

        if not result:
            return await ctx.send("Failed To Change Name File")
        return await ctx.message.add_reaction("✅")

    @commands.command(alises=("w",))
    async def write(self, ctx: commands.Context, *, text: str):
        """ Write to current file, you can type anything """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed()

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)

        user_file = user.current_file
        embed = discord.Embed(colour=discord.Colour.blue())

        try:
            with open(user_file, "w") as file:
                await self.bot.loop.run_in_executor(None, file.write, text)
            embed.title = f"Succes {self.bot.APPLY_EMOJI}"
            embed.description = f"Writed to current file, check it with command, {self.bot.command_prefix}cf."
        except FileNotFoundError:
            embed.title = f"ERROR, {self.bot.X_EMOJI}"
            embed.description = "Error, file not exists"
        except UnicodeEncodeError:
            embed.title = f"ERROR {self.bot.X_EMOJI}"
            embed.description = "You try write to file, emoji or something like this, its unacceptable"
        return await ctx.send(embed=embed)

    @commands.command(aliases=("cf",))
    async def current_file(self, ctx: commands.Context):
        """ get current user file """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed(colour=discord.Colour.blue())

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)

        return await ctx.send(f"Your current file ```{user.current_file}```")

    @commands.command(aliases=("rm", "remove_file", "remove"))
    async def rm_file(self, ctx: commands.Context, *, files: str):
        """
        remove selected file, be cary about it!

        You can select more 1 file, example:
        ```
        >> rm_file lol.py file.py kak.py hello.py
        ```
        but cary about it, because it can be deleted forever
        """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send(f"Type {self.bot.command_prefix}start, and come here again")

        try:
            for file in files:
                if not os.path.exists(f"{user.user_path}/{file}"):
                    await ctx.send("**FNE**(**F**ile **N**ot **E**xists)")
                    return await ctx.message.add_reaction("❌")
                await self.fm.remove_file(file, user)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")


    @commands.command()
    async def mkdir(self, ctx: commands.Context, path: str, *, name: str):
        """ make dir in any directory! only owner """
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send("You Not Authed")

        elif not user.is_owner:
            raise commands.MissingPermissions("Missing Owner permissions")

        loop = self.bot.loop

        to_create = f"{path}/{name}"
        try:
            await loop.run_in_executor(None, os.mkdir, to_create)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send("Failed creating folder!")
            await self.bot.error_channel.send(e)

    @commands.command(aliases=["create_file"])
    @commands.cooldown(20, 2000, commands.BucketType.guild)
    async def touch(self, ctx: commands.Context, name: str, *, type_: str="py"):
        """ create file in your folder """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        if not user:
            embed = discord.Embed(colour=discord.Colour.blue())

            embed.title = "You dont authorizated"
            embed.description = f"Type {self.bot.command_prefix}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)

        if len(name) >= 78:
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

    @commands.command(aliases=["list", "list_files"])
    @commands.cooldown(30, 200, commands.BucketType.guild)
    async def ls(self, ctx: commands.Context, flags: str=None, *, member: discord.Member=None):
        """
        List files, with flags

        -A: get all files with info,
        command get sorted files,
        example:
        ```
        Files:    size:   updated_at:
        justd.py   23KB   1923.12.30 12:23:30
        dod.py    12KB    1923.12.23 23:43:23
        kik.js    90KB    1923.12.29 16:22:32
        ```
        """
        if not member:
            user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        else:
            user = await self.bot.uapi.get_user_by_id(member.id)

        if not user:
            embed = discord.Embed(colour=discord.Colour.blue())

            embed.title = "User didnt authorizated"
            embed.description = f"Type {PREFIX}start,\n for start if you didnt started"

            return await ctx.send(embed=embed)
        all_files = await self.bot.loop.run_in_executor(None, os.listdir, user.user_path)

        if not flags:
            await ctx.send(embed=discord.Embed(
                title=f"All files in your directory",
                description="\n".join(all_files),
                colour=discord.Colour.blue(),
            ))
            return

        if not flags in ["-A", "-a"]:
            return await ctx.send_help(ctx.command)

        embed = discord.Embed(title="All files", colour=discord.Colour.blue())
        files_sorted_by_size = sorted(self.get_files_info(f"{user.user_path}/"), reverse=True, key=lambda x: x[1].st_size)
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

def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))

