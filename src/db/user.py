import discord
from sqlalchemy import sql

from .base import BaseModel, db
from data.base_cfg import BASE_PATH

class User(BaseModel):
    """
    id: int
    user_id: int
    user_name: str
    current_state=None
    current_file: str
    """
    __tablename__ = 'users'

    query: sql.Select

    id = db.Column(db.Integer(), db.Sequence("user_id_seq"), primary_key=True)
    user_id = db.Column(db.BigInteger())
    username = db.Column(db.String(200))
    current_file = db.Column(db.String(100))
    user_path = db.Column(db.String(200))

    def __repr__(self):
        return "<Users id='{0.id}', user_id='{0.user_id}', name='{0.name}', user_path='{0.user_path}'>".format(self)

class UserApi:
    @staticmethod
    async def get_user_by_id(user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    @staticmethod
    async def add_new_user(user: discord.User, guild: discord.Guild):
        old_user = await User.query.where(User.user_id == user.id).gino.first()

        if old_user:
            return old_user

        new_user = User()

        if not guild:
            new_user.user_path = fr"\{BASE_PATH}\{user.name}"
            new_user.current_file = fr"\{BASE_PATH}\{user.name}"
        else:
            new_user.user_path = fr"\{BASE_PATH}\guild_{guild.id}\{user.name}"
            new_user.current_file = fr"\{BASE_PATH}\guild_{guild.id}\{user.name}\main.py"

        new_user.user_id = user.id
        new_user.username = user.name
        
        await new_user.create()
        return new_user
