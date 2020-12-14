from pathlib import Path

from sqlalchemy import ForeignKey
import discord
# here guild register
from .base import BaseModel, db
from data.base_cfg import BASE_PATH


class Guild(BaseModel):
    __tablename__ = 'guilds'

    query: db.sql.Select

    id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    guild_id = db.Column(db.Integer)
    guild_name = db.Column(db.String(200))
    config = ForeignKey('Config')

    def __repr__(self):
        return "<Guild(id='{0.id}', guild_id='{0.guild_id}', guild_name='{0.guild_name}'".format(self)


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

        await new_guild.create()
        return new_guild

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

        return f"{BASE_PATH}guild_{guild.id}"
