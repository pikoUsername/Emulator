import discord
from sqlalchemy import sql

from .base import TimedBaseModel, db
from src.config import BASE_PATH


class User(TimedBaseModel):
    """No help"""
    __tablename__ = "user2"

    id = db.Column(db.Integer(), db.Sequence("users_id_seq"), primary_key=True)
    user_id = db.Column(db.BigInteger())
    username = db.Column(db.String(200))
    current_file = db.Column(db.String(100))
    user_path = db.Column(db.String(200))
    is_owner = db.Column(db.Boolean, default=True)

    @staticmethod
    async def get_user_by_id(user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    @staticmethod
    async def add_new_user(user: discord.User, guild: discord.Guild = None):
        """
        Here must be a check, and DM mode
        create user folder for redacting

        :param user:
        :param guild:
        :return:
        """
        old_user = await User.query.where(User.user_id == user.id).gino.first()

        if old_user:
            return old_user

        new_user = User()

        if not guild:
            new_user.user_path = fr"{BASE_PATH}\{user.name}"
            new_user.current_file = fr"{BASE_PATH}\{user.name}\main.py"
        else:
            new_user.user_path = fr"{BASE_PATH}\guild_{guild.id}\{user.name}"
            new_user.current_file = fr"{BASE_PATH}\guild_{guild.id}\{user.name}\main.py"

        new_user.user_id = user.id
        new_user.username = user.name
        await new_user.create()

        return new_user

    @staticmethod
    async def get_all_owners():
        all_owners = await User.query.where(User.is_owner is True).gino.all()
        return all_owners
