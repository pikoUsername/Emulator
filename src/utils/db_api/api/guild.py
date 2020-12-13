
import discord
# here guild API, get_guild
from src.utils.db_api.models.guild import Guild

class GuildAPI:
    @staticmethod
    async def get_guild(guild_id: int):
        guild = Guild.query.where(Guild.guild_id == guild_id).gino.first()
        return guild

    async def add_guild(self, guild: discord.Guild):
        old_guild = await self.get_guild(guild.id)

        if old_guild:
            return old_guild

        new_guild = Guild()
        new_guild.guild_id = guild.id
        new_guild.guild_name = guild.name


    async def change_config_guild(self, guild: discord.Guild):
        pass

    async def create_guild_folder(self, guild: discord.Guild):
        guild_ = await self.get_guild(guild.id)

        if guild_ is None:
            await self.add_guild(guild)

