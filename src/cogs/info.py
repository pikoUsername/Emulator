from datetime import datetime
import time
import sys
from typing import Union

from discord.ext import commands
import discord

from ..models import User, reg_user
from ..utils.cache import async_cache
from src.config import PREFIX


class DiscordInfo(commands.Cog):
    __slots__ = ("bot")
    """ Info about bot and etc. """
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not ctx.guild:
            return False

        return True


    @commands.command(aliases=("?",))
    async def info(self, ctx: commands.Context):
        """ get Info about Bot """

        text = (
            "Hello, i m bot, and i must simulate text redactor",
            "I can make basic operations with files, delete, open, rewrite\n",
            f"You can start using me with command {PREFIX}start",
        )
        e = discord.Embed(title="Information",
                          description="\n".join(text))
        e.add_field(name="Python version",
                    value=f"{sys.version_info.major}.{sys.version_info.minor}")
        e.add_field(name="Author",
                    value="piko#0381")
        e.add_field(name="Github",
                    value="[here](https://github.com/pikoUsername/Emulator)")
        e.add_field(name="Library",
                    value="[discord.py](https://github.com/Rapptz/discord.py)")
        e.set_footer(text=f"requested by {ctx.author.display_name} || {datetime.utcnow()}",
                     icon_url=ctx.author.avatar_url),
        await ctx.send(embed=e)

    @commands.command()
    async def profile(
            self, ctx: commands.Context, member: Union[discord.Member, int, str, discord.User] = None
    ):
        user_id = member if isinstance(member, (str, int)) else member.id
        if member is None:
            user_id = ctx.author.id

        user = await User.get_user_by_id(user_id)
        if not user:
            _, user = await reg_user(ctx, check=False)
        # todo profile

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """ Pong """
        first_time = time.time()

        message = await ctx.send("...")
        ping = int(self.bot.latency * 1000)

        second_time = first_time - time.time()
        text = (
            f"Message Ping: {int(second_time + ping)}",
            f"Bot Latency: {ping}",
        )
        embed = discord.Embed(title="Ping",
                              description="\n".join(text))
        await message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    async def file(self, ctx: commands.Context, *, file_: str = None):
        """ Show current file, if you set file, then show file text """
        user = await User.get_user_by_id(ctx.author.id)
        if not user:
            _, user = await reg_user(ctx, check=False)
        embed = discord.Embed()
        file_to_read = f"{user.current_file}/{file_}" if file_ else user.current_file

        with open(file_to_read, "r") as file:
            lines = file.read()
            if len(lines) >= 2048:
                return await ctx.send("File too long")

        embed.title = f"Text of file: {file_}"
        text = (
            f"```{lines}```",
        )
        embed.description = "\n".join(text)
        embed.set_footer(text=f"Current file: ../../{user.current_file[:-10]}")
        await ctx.send(embed=embed)

    @commands.command()
    async def time(self, ctx: commands.Context):
        """ Get time """
        await ctx.send(embed=discord.Embed(
            title="Time",
            description=f"Time: {datetime.utcnow()} :timer:",
        ).set_footer(text=f"requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url))

    @commands.command()
    @async_cache()
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        """ Gets Avatar of author. """
        embed = discord.Embed()
        user = user or ctx.author
        avatar = user.avatar_url_as(static_format='png')
        embed.set_author(name=str(user), url=avatar)
        embed.set_image(url=avatar)
        return await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """ Invite bot. """
        perms = discord.Intents().none()
        perms.messages = True
        perms.read_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.add_reactions = True
        perms.attach_files = True

        await ctx.send(
            embed=discord.Embed(title="Invite",
                                description="[Click here to invite]"
                                            f"({discord.utils.oauth_url(self.bot.client_id, perms)})"))


def setup(bot):
    bot.add_cog(DiscordInfo(bot))
