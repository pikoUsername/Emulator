import discord

from .base import TimedBaseModel, db
from .guild import Guild
from ..config import BASE_PATH
from ..utils.file_manager import FileManager


class User(TimedBaseModel):
    __tablename__ = "user2"

    id = db.Column(db.Integer(), db.Sequence("users_id_seq"), primary_key=True)
    user_id = db.Column(db.BigInteger())
    username = db.Column(db.String(200))
    current_file = db.Column(db.String(100))
    user_path = db.Column(db.String(200))
    is_owner = db.Column(db.Boolean, default=True)

    async def get_user_by_id(self, user_id):
        try:
            user = self.get_current()
        except LookupError:
            user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self, user: discord.User, guild: discord.Guild):
        """
        Here must be a check, and DM mode
        create user folder for redacting

        :param user:
        :param guild:
        :return:
        """
        old_user = await User.get_current()

        if old_user:
            return old_user

        new_user = User()

        new_user.user_path = fr"{BASE_PATH}\guild_{guild.id}\{user.name}"
        new_user.current_file = fr"{BASE_PATH}\guild_{guild.id}\{user.name}\main.py"

        new_user.user_id = user.id
        new_user.username = user.name

        await new_user.create()
        await self.create_files(user, guild.id)
        return new_user

    @staticmethod
    async def create_files(user: 'User', guild_id: int):
        guild = await Guild.get_guild(guild_id)
        fm = FileManager.get_current()
        if not guild:
            return await fm.create_user_folder(user)
        await fm.create_user_folder(user=user)
        await fm.create_file(file_name="main", user=user)

    @staticmethod
    async def get_all_owners():
        all_owners = await User.query.where(User.is_owner is True).gino.all()
        return all_owners
