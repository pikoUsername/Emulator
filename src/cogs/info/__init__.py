from datetime import datetime
import sys
import os


from discord.ext import commands
import discord

class DiscordInfo(commands.Cog):
    """ Info about bot and etc. """
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
            description="\n".join(text))
        .add_field(name="Python version", value=f"{sys.version_info.major}.{sys.version_info.minor}")
        .add_field(name="Author", value="piko#0381")
        .add_field(name="Github", value="(Here)[https://github.com/pikoUsername/Emulator]")
        .add_field(name="Library", value="(discord.py)[https://github.com/Rapptz/discord.py]")
        .set_footer(text=f"requested by {ctx.author.display_name} || {datetime.utcnow()}",
                    icon_url=ctx.author.avatar_url),
        )

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """ Pong """
        ping = str(self.bot.latency * 1000)
        return await ctx.send(f"Ping - {ping[0:10]}")

    @commands.command()
    @commands.guild_only()
    async def about_file(self, ctx: commands.Context, *, file: str):
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)
        embed = discord.Embed()

        if not user:
            embed.title = f"You not authorizated {self.bot.X_EMOJI}"
            embed.description = "No access for files"
            return await ctx.send(embed=embed)

        file_to_read = f"{user.user_path}/{file}"

        if not os.path.exists(file_to_read):
            return await ctx.send("File not Exists!")

        try:
            with open(file_to_read, "r") as file:
                lines = file.read()
                if len(lines) >= 2048:
                    return await ctx.send("File too long")

            embed.title = f"Succes, {self.bot.APPLY_EMOJI}"
            text = [
                f"{lines}",
            ]
            embed.description = "\n".join(text)
        except Exception as e:
            embed.title = f"ERROR, {self.bot.X_EMOJI}"
            embed.description = e
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
        await ctx.send(embed=discord.Embed(title="Invite",
                                           description=f"[Click here to invite](https://discord.com/api/oauth2/authorize?client_id=751682699160191109&permissions=149504&scope=bot)"))

def setup(bot):
    bot.add_cog(DiscordInfo(bot))
