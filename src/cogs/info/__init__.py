from datetime import datetime

from discord.ext import commands
import discord

class DiscordInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["?"])
    async def info(self, ctx: commands.Context):
        """ get Info about Bot """

        text = [
            "Hello, i m bot, and i must simulate text redactor",
            "I can make basic operations with files, delete, open, rewrite",
            " ",
            f"You can start using me with command {self.bot.command_prefix}start",
        ]

        await ctx.send(embed=discord.Embed(
            title="Information",
            description="\n".join(text)
        ).add_field(name="Python version", value="3.8.3").add_field(name="Author", value="piko#0381")
        .add_field(name="Github", value="https://github.com/pikoUsername/Emulator")
        .set_footer(text=f"requested by {ctx.author.display_name} || {datetime.utcnow()}",
                    icon_url=ctx.author.avatar_url)
        )

    @commands.command()
    async def time(self, ctx: commands.Context):
        """ Get time """
        await ctx.send(embed=discord.Embed(
            title="Time",
            description=f"Time: {datetime.utcnow()} :timer:",
        ).set_footer(text=f"requested by {ctx.author.display_name}",icon_url=ctx.author.avatar_url))

    @commands.command()
    async def avatar(self, ctx: commands.Context, *, member: discord.Member):
        """ Gets Avatar of author """
        if not member:
            await ctx.send(embed=discord.Embed(
                title=f"Avatar {ctx.author.display_name}",
            ).set_image(url=ctx.author.avatar_url))

        await ctx.send(embed=discord.Embed(
            title=f"Avatar {member.display_name}",
        ).set_image(url=member.avatar_url))

def setup(bot):
    bot.add_cog(DiscordInfo(bot))
