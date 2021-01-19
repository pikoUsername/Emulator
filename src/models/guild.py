import asyncio
import os
import os.path

from sqlalchemy import sql
import discord

from src.models.base import BaseModel, db
from data.config import BASE_PATH, PREFIX


class Guild(BaseModel):
    __tablename__ = 'guilds2'

    query: sql.Select

    id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    guild_id = db.Column(db.BigInteger)
    guild_name = db.Column(db.String(200))
    command_prefix = db.Column(db.String(20), default=PREFIX)


class GuildAPI:
    @staticmethod
    async def get_guild(guild_id: int):
        guild = await Guild.query.where(Guild.guild_id == guild_id).gino.first()
        return guild

    async def add_guild(self, guild: discord.Guild): # guild examplar
        old_guild = await self.get_guild(guild.id)

        if old_guild:
            return old_guild

        new_guild = Guild()
        new_guild.guild_id = guild.id
        new_guild.guild_name = guild.name

        await self.create_guild_folder(guild)
        await new_guild.create()
        return new_guild

    async def create_guild_folder(self, guild: discord.Guild):  # create folder in FILES path, and file path ll base on guild.id
        await self.add_guild(guild)
        # here creating folder
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, os.mkdir, fr"{BASE_PATH}\guild_{guild.id}")

    async def get_guild_path(self, guild: discord.Guild):
        guild_ = await self.get_guild(guild.id)

        if not guild_:
            await self.create_guild_folder(guild)

        return fr"{BASE_PATH}\\guild_{guild.id}"
