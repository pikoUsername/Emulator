from datetime import datetime
import sys
import os

from discord.ext import commands
import discord

from data.base_cfg import PREFIX

class DiscordInfo(commands.Cog):
    """ Info about bot and etc. """
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    @commands.command(aliases=["?"])
    async def info(self, ctx: commands.Context):
        """ get Info about Bot """

        text = [
            "Hello, i m bot, and i must simulate text redactor",
            "I can make basic operations with files, delete, open, rewrite",
            " ",
            f"You can start using me with command {PREFIX}start",
        ]
        e = discord.Embed(title="Information", description="\n".join(text))
        e.add_field(name="Python version", value=f"{sys.version_info.major}.{sys.version_info.minor}")
        e.add_field(name="Author", value="piko#0381")
        e.add_field(name="Github", value="[here](https://github.com/pikoUsername/Emulator)")
        e.add_field(name="Library", value="[discord.py](https://github.com/Rapptz/discord.py)")
        e.set_footer(text=f"requested by {ctx.author.display_name} || {datetime.utcnow()}",
                    icon_url=ctx.author.avatar_url),
        await ctx.send(embed=e)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """ Pong """
        ping = str(self.bot.latency * 1000)
        return await ctx.send(f"Ping - {ping[0:10]}")

    @commands.command()
    async def file(self, ctx: commands.Context, *, file_: str=None):
        """ Show current file, if you set file, then show file text """
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        embed = discord.Embed()

        if not user:
            embed.title = f"You not authorizated {self.bot.X_EMOJI}"
            embed.description = "No access for files"
            return await ctx.send(embed=embed)
        if not file_:
            file_to_read = f"{user.current_file}"
        else:
            file_to_read = f"{user.user_path}/{file_}"

        if not os.path.exists(file_to_read):
            return await ctx.send("File not Exists!")

        try:
            with open(file_to_read, "r") as file:
                lines = file.read()
                if len(lines) >= 2048:
                    return await ctx.send("File too long")

            embed.title = f"Text of file: {file_}"
            text = [
                f"```{lines}```",
            ]
            embed.description = "\n".join(text)
        except Exception as e:
            embed.title = f"ERROR, {self.bot.X_EMOJI}"
            embed.description = e
        embed.set_footer(text=f"Current file: {user.current_file}")
        await ctx.send(embed=embed)

    @commands.command()
    async def time(self, ctx: commands.Context):
        """ Get time """
        await ctx.send(embed=discord.Embed(
            title="Time",
            description=f"Time: {datetime.utcnow()} :timer:",
        ).set_footer(text=f"requested by {ctx.author.display_name}",icon_url=ctx.author.avatar_url))

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: discord.Member=None):
        """ Gets Avatar of author """
        if not member:
            await ctx.send(embed=discord.Embed(
                title=f"Avatar {ctx.author.display_name}",
            ).set_image(url=ctx.author.avatar_url))
            return

        await ctx.send(embed=discord.Embed(
            title=f"Avatar {member.display_name}",
        ).set_image(url=member.avatar_url))

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """ Invite bot """
        perms = discord.Intents()
        perms.messages = True
        perms.read_messages = True
        perms.embed_links = True
        perms.read_message_history = True
        perms.add_reactions = True
        perms.attach_files = True

        await ctx.send(embed=discord.Embed(title="Invite",
                                           description=f"[Click here to invite]({discord.utils.oauth_url(self.bot.client_id, perms)})"))

    @commands.command()
    async def bug_report(self, ctx: commands.Context, command: str=None, *, text: str):
        """Bug report"""
        if not text:
            return await ctx.send("Describe a BUG or something like this")

        error_channel = getattr(self.bot, 'error_channel')

        embed = discord.Embed(title="Report Bug")
        embed.add_field(name=f"Command, {command}", value=f"Report: \n{text}")

        try:
            await error_channel.send(embed=embed)
        except TypeError:
            pass

def setup(bot):
    bot.add_cog(DiscordInfo(bot))

