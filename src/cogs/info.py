from datetime import datetime
import time
import sys

from discord.ext import commands
import discord

from ..utils.cache import async_cache
from src.config import PREFIX


class DiscordInfo(commands.Cog):
    __slots__ = "bot",
    """ Info about bot and etc. """
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
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
    async def ping(self, ctx: commands.Context):
        """ Pong """
        first_time = time.perf_counter()

        message = await ctx.send("...")
        ping = int(self.bot.latency * 1000)

        second_time = first_time - time.perf_counter()
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
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        embed = discord.Embed()
        file_to_read = f"{user.current_file}/{file_}" or user.current_file

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

        await ctx.send(embed=discord.Embed(title="Invite",
                                           description=f"[Click here to invite]({discord.utils.oauth_url(self.bot.client_id, perms)})"))

    @commands.command()
    async def select(self, ctx: commands.Context, *, user_id: int = None):
        """ Get Selected User."""
        user_id = user_id or ctx.author.id
        user = await self.bot.uapi.get_user_by_id(user_id)
        try:
            embed = discord.Embed(
                title="Selected User",
                description=f"name: {user.username}\nis owner: {user.is_owner}\ncurrent_file: {user.current_file}"
                            f"\nuser path: {user.user_path}\ncreated at: {user.created_at}")
        except AttributeError:
            return await ctx.send("User Not Authed as User")
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordInfo(bot))
