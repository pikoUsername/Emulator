from pathlib import Path

import discord
# here guild API, get_guild
from src.utils.db_api.models.guild import Guild

class GuildAPI:
    @staticmethod
    async def get_guild(guild_id: int):
        guild = Guild.query.where(Guild.guild_id == guild_id).gino.first()
        return guild

    async def add_guild(self, guild: discord.Guild): # guild examplar
        old_guild = await self.get_guild(guild.id)

        if old_guild:
            return old_guild

        new_guild = Guild()
        new_guild.guild_id = guild.id
        new_guild.guild_name = guild.name


    async def change_config_guild(self, guild: discord.Guild):
        pass

    async def create_guild_folder(self, guild: discord.Guild): # create folder in FILES path, and file path ll base on guild.id
        await self.add_guild(guild)

        # here creating folder
        pass

    async def get_guild_path(self, guild: discord.Guild):
        guild_ = await self.get_guild(guild.id)

        if not guild_:
            await self.create_guild_folder(guild)

        base_path = str(Path(__name__).parent.parent / "files")
        return f"{base_path}/{guild.id}"




