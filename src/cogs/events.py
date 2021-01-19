import sys

from discord.ext import commands
from discord.ext.commands import errors
import discord
from loguru import logger

from src.models import Guild, GuildAPI
from ..utils.notify import notify_all_owners


class DiscordEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await notify_all_owners(self.bot, text="BOT STARTED")

    @commands.Cog.listener()
    async def on_message_edit(self, after, before):
        """ Handler for edited messages, re-executes commands """
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        guild = await Guild.query.where(guild.id == Guild.guild_id).gino.first()

        if not guild:
            gapi = GuildAPI()
            await gapi.add_guild(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        g_id = str(guild.id)
        async with self.bot.pool.acquire() as connection:
            await self.bot.fm.delete_all_guild_files(g_id)
            await connection.first(
                """
                    DELETE FROM guilds2
                    WHERE (guild_id = $1);
                """,
                g_id)
            logger.info(f"leaved and deleted thats guild folder")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            logger.exception(f"{err}, {sys.exc_info()}")

            # await self.error_channel.send(file=file)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(embed=discord.Embed(
                title="Error on processing Command",
                description=f"error: \n```{err}```",
                ), delete_after=30)

        elif isinstance(err, errors.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title=f"Fail {self.bot.X_EMOJI}",
                description="Permission ERROR",
            ))

        elif isinstance(err, errors.CheckFailure):
            await ctx.send(embed=discord.Embed(
                title=f"Fail {self.bot.X_EMOJI}",
                description="You cant made this",
            ))

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...", delete_after=30)

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cool down... try again in {err.retry_after:.2f} seconds.", delete_after=30)

        elif isinstance(err, errors.CommandNotFound):
            pass

        elif isinstance(err, errors.NoPrivateMessage):
            await ctx.send(embed=discord.Embed(title="Private message Not work",
                                               description="Bot work only in guild channels"))

        else:
            logger.exception(err)
            await self.bot.send_error(ctx, err)


def setup(bot):
    bot.add_cog(DiscordEvents(bot))
