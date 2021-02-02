import discord
from gino import GinoConnection

from .base import TimedBaseModel, db
from .guild import Guild
from ..config import BASE_PATH
from ..utils.file_manager import FileManager


__all__ = ("User", "reg_user", "create_files")


async def create_files(guild_id: int, *, user: 'User' = None, user_id: int = None):
    if user_id:
        user = await User.get_user_by_id(user_id)

    fm = FileManager.get_current()
    guild = await Guild.get_guild(guild_id)
    if not guild:
        await fm.create_guild_folder(guild_id)
    await fm.create_user_folder(user.user_path, user.user_id)
    await fm.create_file(file_name="main", user_path=user.user_path)


class User(TimedBaseModel):
    __tablename__ = "user2"

    id = db.Column(db.Integer(), db.Sequence("users_id_seq"), primary_key=True, index=True)
    user_id = db.Column(db.BigInteger(), index=True)
    username = db.Column(db.String(200))
    current_file = db.Column(db.String(100))
    user_path = db.Column(db.String(200))
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
            return old_user

        new_user = User()

        new_user.user_path = fr"{BASE_PATH}\guild_{guild.id}\user_{user.id}"
        new_user.current_file = fr"{BASE_PATH}\guild_{guild.id}\user_{user.id}\main.py"

        new_user.user_id = user.id
        new_user.username = user.name

        await new_user.create()

        await create_files(guild.id, user=new_user)

        return new_user

    @staticmethod
    async def get_all_owners():
        all_owners = await User.query.where(User.is_owner is True).gino.all()
        return all_owners


async def reg_user(ctx, user: User = None, check: bool = True) -> [bool, User]:
    user = user or await User.add_new_user(ctx.author, ctx.guild)
    if user and check:
        return False, None
    # await ctx.send(embed=discord.Embed(title=f"Success :white_check_mark:",
    #                                    description="Success created folder with ur name!",
    #                                    colour=discord.Colour.blue()))
    return True, user
