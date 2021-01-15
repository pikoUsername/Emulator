from typing import Union
import os

import discord


class DBC:
    __slots__ = ("get_user", "bot", "add_new_user")

    def __init__(self, bot):
        self.bot = bot

    async def get_user(self, user_id: int):
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                user = await connection.fetchrow("SELECT u.* FROM users u WHERE user_id = $1", user_id)
        return user

    async def add_new_user(self, user: Union[discord.User, discord.Member]):
        is_owner = False
        if user.id in self.bot.data['bot']['OWNER_IDS']:
            is_owner = True

        async with self.bot.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO users(user_id, name, current_file, user_path, is_owner) 
                    VALUES ($1, $2, $3, $4, $5);
                """, user.id, user.name,
                fr"{self.bot.data['bot']['BASE_PATH']}\guild_{user.guild.id}\user_{user.id}\main.py",
                fr"{self.bot.data['bot']['BASE_PATH']}\guild_{user.guild.id}\user_{user.id}",
                is_owner)

    async def update_user(self, user_id: int, *update_kwargs):
        async with self.bot.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    'INSERT INRO '
                )

    async def delete_user(self, user_id: int, guild_id):
        user = await self.get_user(user_id)
        if not user:
            raise AttributeError("User Not Exists")


