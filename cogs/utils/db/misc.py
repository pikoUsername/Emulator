from typing import Union

import discord


class DBC:
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    async def add_new_user(self, user: Union[discord.User, discord.Member], guild: discord.Guild):
        is_owner = False
        if user.id in self.bot.data['bot']['OWNER_IDS']:
            is_owner = True
        data = self.bot.data['bot']

        async with self.bot.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO users(user_id, name, current_file, user_path, is_owner) 
                    VALUES ($1, $2, $3, $4, $5);
                """, user.id, user.name,
                fr"{data['BASE_PATH']}\guild_{user.guild.id}\user_{user.id}\main.py",
                fr"{data['BASE_PATH']}\guild_{user.guild.id}\user_{user.id}",
                is_owner)

        await self.bot.fm.create_user_folder(user.id, guild.id)

    async def add_new_guild(self, guild: discord.Guild):
        """Add New User Based Discord.py Guild Class"""
        g_id = guild.id
        async with self.bot.bind.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    'INSERT INTO guilds(guild_id, guild_name) VALUES ($1, $2);', g_id, guild.name
                )

    async def delete_user(self, user_id: int, guild_id: int):
        """Delete User model with folder"""
        async with self.bot.bind.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    'DELETE FROM users u WHERE u.user_id = $1', user_id
                )
                await self.bot.fm.delete_user_folder(user_id, guild_id)

    async def remove_guild(self, guild_id: int):
        """
        Remove Selected Guild Model, but not delete files.
        """
        async with self.bot.bind.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    'DELETE FROM guilds g WHERE g.guild_id = $1', guild_id
                )
