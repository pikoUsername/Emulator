from discord.ext import commands
from loguru import logger


class Events(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err):
        missing_pems = (commands.BotMissingPermissions, commands.MissingPermissions)
        ignore_errors = (
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.TooManyArguments,
            commands.BadUnionArgument
        )
        if isinstance(err, ignore_errors):
            await ctx.send_help(ctx.command)

        elif isinstance(err, missing_pems):
            await ctx.send("**M**issing **R**equired **P**ermissions")

        elif isinstance(err, commands.CommandInvokeError):
            logger.error(err)
            await self.bot.create_error_letter(err, ctx)
        elif isinstance(err, commands.CommandNotFound):
            pass
        else:
            logger.error(err)

    @commands.Cog.listener()
    async def on_message_edit(self, after, before):
        """ Handler for edited messages, re-executes commands """
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        g_id = guild.id
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO guilds(
                        guild_id, 
                        guild_name
                    ) VALUES ($1, $2)
                """, g_id, guild.name)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        pass

def setup(bot):
    bot.add_cog(Events(bot))