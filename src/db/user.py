import discord

from .base import BaseModel, db

class User(BaseModel):
    """
    id: int
    user_id: int
    user_name: str
    current_state=None
    current_file: str
    """
    __tablename__ = 'users'

    query: db.sql.Select

    id = db.Column(db.Integer(), db.Sequence("user_id_seq"), primary_key=True)
    user_id = db.Column(db.Integer())
    username = db.Column(db.String(200))
    current_file = db.Column(db.String(100))
    current_path = db.Column(db.String(200))
    # current_state = db.Column(db.String())

    def __repr__(self):
        return "<Users id='{0.id}', user_id='{0.user_id}', name='{0.name}', user_path='{0.user_path}'>".format(self)

class UserApi:
    @staticmethod
    async def get_user_by_id(user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self, user: discord.User, guild: discord.Guild):
        old_user = await self.get_user_by_id(user.id)

        if old_user:
            return old_user

        new_user = User()
        new_user.current_path = f"guild_{guild.id}/{user.name}"
        new_user.user_id = user.id
        new_user.username = user.name
        new_user.current_file = None
        
        await new_user.create()
        return new_user
