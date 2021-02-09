import os

import discord
from gino import GinoConnection

from .base import TimedBaseModel, db
from .guild import Guild
from ..config import BASE_PATH

from ..utils.misc import create_path

__all__ = ("User", "reg_user")


class User(TimedBaseModel):
    __tablename__ = "user2"

    id = db.Column(db.Integer(), db.Sequence("users_id_seq"), primary_key=True, index=True)
    user_id = db.Column(db.BigInteger(), index=True)
    username = db.Column(db.String(200))
    is_owner = db.Column(db.Boolean, default=False)

    @staticmethod
    async def get_user_by_id(user_id: int):
        async with db.acquire() as conn:
            conn: GinoConnection = conn
            user = await conn.first(f"SELECT * FROM {User.__tablename__} WHERE user_id = $1;", user_id)
        return user

    @staticmethod
    async def add_new_user(user: discord.User, guild: discord.Guild):
        """
        Here must be a check, and DM mode
        create user folder for redacting

        :param user:
        :param guild:
        :return:
        """
        old_user = await User.get_user_by_id(user.id)

        if old_user:
            user_path = create_path(guild.id, user.id)

            return old_user

        new_user = User()
        # new_user.user_path = fr"{BASE_PATH}\guild_{guild.id}\user_{user.id}"
        new_user.current_file = fr"{BASE_PATH}\guild_{guild.id}\user_{user.id}\main.py"
        new_user.user_id = user.id
        new_user.username = user.name
        await new_user.create()

        return new_user

    @staticmethod
    async def get_all_owners():
        all_owners = await User.query.where(User.is_owner is True).gino.all()
        return all_owners


async def reg_user(ctx, user: User = None, check: bool = True) -> [bool, User]:
    user = user or await User.add_new_user(ctx.author, ctx.guild)
    if user and check:
        return False, None
    return True, user
