import discord
from discord.ext import commands
from loguru import logger

#
class HelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__(
            width=90, sort_commands=True, dm_help=True, indent=4,
        )

    async def on_help_command_error(self, ctx, error):
        async with ctx.bot.message_lock(ctx.message):
            try:
                await self.handle_error(ctx, error)
            except discord.NotFound:
                pass

    async def handle_error(self, ctx, error):
        reported = False

        if isinstance(error, commands.errors.CommandInvokeError):
            error = error.__cause__

            if isinstance(error, discord.Forbidden):
                logger.debug(
                    "Lacks permissions to send help to %s (%d)",
                    ctx.author.id,
                )

                embed = discord.Embed(colour=discord.Colour.red())
                embed.title = "Cannot send help command"
                embed.description = (
                    "You do not allow DMs from this server. "
                    "Please enable them so help information can be sent."
                )

                reported = True
                await ctx.send(embed=embed)

        # Default error handling
        if not reported:
            logger.error("Unexpected error raised during help command", exc_info=error)
            await ctx.bot.report_other_exception(
                ctx, error, "Unexpected error occurred during help command!",
            )