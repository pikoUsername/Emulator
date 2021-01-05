from discord.ext import commands
import discord
from loguru import logger

from src.models import Guild, GuildAPI, UserApi
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
            async with connection.transaction():
                await self.bot.fm.delete_all_guild_files(g_id)
                await connection.execute(
                    """
                        DELETE FROM guilds2
                        WHERE (server_id = $1) ;
                    """,
                    g_id)
            logger.info(f"leaved and deleted thats guild folder")


def setup(bot):
    bot.add_cog(DiscordEvents(bot))
