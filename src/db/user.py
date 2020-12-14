from .base import BaseModel, db

class User(BaseModel):
    """
    id: int
    user_id: int
    user_name: str
    current_state=None
    current_file: str
    user_path: {guild.id}/{username}/
    """
    __tablename__ = 'users'

    query: db.sql.Select

    id = db.Column(db.Integer(), db.Sequence("user_id_seq"), primary_key=True)
    user_id = db.Column(db.Integer())
    username = db.Column(db.String(200))
    current_state = db.Column(db.String())

    def __repr__(self):
        return "<Users id='{0.id}', user_id='{0.user_id}', name='{0.name}', user_path'{0.user_path}'>".format(self)

class UserApi:
    async def get_user_by_id(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    # Todo: Make a get_current function