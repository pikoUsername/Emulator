import asyncio
import os
from os.path import join

import aiofiles
from discord.ext import commands
from loguru import logger
import discord

from src.utils.file_manager import FileManager
from .utils.upload import load_code_from_github
from src.models import User, reg_user, create_files
from src.config import BASE_PATH

__all__ = ("setup",)

from ...utils.misc import create_path


class TextRedacotorCog(commands.Cog, name="Redactor"):
    __slots__ = ("bot", "fm")
    """Files Redactor..."""
    def __init__(self, bot):
        self.bot = bot
        self.fm = FileManager.get_current()

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command cannot be used in private messages.')
        return True

    @commands.command()
    async def upload_from_github(self, ctx: commands.Context, owner: str, repo: str, branch: str = "master"):
        """
        Create Repo In Your User Directory, And Its Not Working.
        """
        user_path = str(create_path(ctx.guild.id, ctx.author.id))
        await load_code_from_github(owner, repo, user_path, branch)

    @commands.command()
    async def go_to_file(self, ctx: commands.Context, *, file: str):
        """
        Set current file, and checks you out
        If you exists, your table current_file changes
        """
        [_, user] = await reg_user(ctx, check=False)

        if not os.path.exists(f"{user.user_path}/{file}"):
            return await ctx.send("File not exists")

        await user.update(current_file=f"{user.user_path}/{file}").apply()
        await ctx.send(embed=discord.Embed(title=f"Success, {self.bot.APPLY_EMOJI}",
                                           description=f"Now your current file is ``{file}``"))

    @commands.command(aliases=("mv",))
    async def move(self, ctx: commands.Context, *, args: str):
        """
        Rename file, have some mods

        ========= ============================
        Chareters Meaning
        --------- ----------------------------
        '-f'      flag for some files
        '-U'      check for unicode
        ========= ============================
        """
        [_, user] = await reg_user(ctx, check=False)

        try:
            result = await self.fm.change_file_name(user.user_path, file, to_change)
        except (FileNotFoundError, PermissionError) as e:
            logger.error(e)
            result = None

        if not result:
            return await ctx.send("Failed To Change Name File")
        return await ctx.message.add_reaction("✅")

    @commands.command(alises=("w",))
    async def write(self, ctx: commands.Context, file: str, *, text: str):
        """
        Write to current file,
        if you do not select file.
        You can type anything.

        * Write to file, not append, this command have some mods

        ========= ===============================================================
        Character Meaning
        --------- ---------------------------------------------------------------
        'append'  append to end of file
        'start'   add text to start of file
        'center'  add to center of file
        'line'    selected line ll re-write
        ========= ===============================================================
        """
        [_, user] = await reg_user(ctx, check=False)

        user_file = file or user.current_file
        embed = discord.Embed(colour=discord.Colour.random())

        try:
            async with aiofiles.open(user_file) as file:
                await self.bot.loop.run_in_executor(None, file.write, text)

            embed.title = f"Succes {self.bot.APPLY_EMOJI}"
            embed.description = f"Writed to current file, check it out with command, {self.bot.command_prefix}cf."
            return await ctx.send(embed=embed)
        except FileNotFoundError:
            pass
        except UnicodeEncodeError:
            pass

    @commands.command(aliases=("rm", "remove_file", "remove"))
    async def rm_file(self, ctx: commands.Context, file: str):
        """
        remove selected file, be cary about it!

        You can select 1 file, example:
        ```
        >> rm_file lol.py
        ```
        but cary about it, because it can be deleted forever
        """
        user = await User.get_user_by_id(ctx.author.id)
        try:
            user.current_file  # check for user ;)
        except AttributeError:
            return await ctx.send(f"Type {self.bot.command_prefix}start, and come here again")

        try:
            await self.fm.remove_file(file, user.user_path)
        except AttributeError:
            return await ctx.message.add_reaction("❌")
        except FileNotFoundError:
            return await ctx.send("File Not Exists")
        await ctx.message.add_reaction("✅")

    @commands.command(aliases=["create_file"])
    @commands.cooldown(10, 200, commands.BucketType.channel)
    async def touch(self, ctx: commands.Context, file_name: str):
        """ create file in your folder """
        if len(file_name) >= 78:
            return
        elif os.path.exists(f"{BASE_PATH}/{file_name}"):
            await ctx.send("this File aleardy exists")

        user_path = create_path(ctx.guild.id, ctx.author.id)
        await self.fm.create_file(file_name=file_name, user_path=user_path)
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
        user_id = member.id if member else ctx.author.id
        user_path = create_path(ctx.guild.id, user_id)

        if not os.path.exists(user_path):
            return await ctx.send("Type Start for to able activate this command")

        loop = asyncio.get_running_loop()
        all_files = await loop.run_in_executor(
            None, os.listdir, user_path)

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
            self.get_files_info(f"{user_path}/"), reverse=True, key=lambda x: x[1].st_size)
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
    async def open_file(self, ctx: commands.Context, file: str = None):
        f = await self.fm.read_file(
            file if file else "main.py",
            str(create_path(ctx.guild.id, ctx.author.id)))
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
        import time
        return time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(dt))


def setup(bot):
    bot.add_cog(TextRedacotorCog(bot))
