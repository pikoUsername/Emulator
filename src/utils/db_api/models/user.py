from .base import BaseModel, db

class User(BaseModel):
    """
    id: int
    user_id: int
    user_name: str
    files_path: File
    file: {files_path}str
    current_state=None
    current_file: str
    user_path: {guild.id}/{username}/
    """
    __tablename__ = 'users'

    query: db.sql.Select

    def __repr__(self):
        return "<Users(id='{0.id}', user_id='{0.user_id}', name='{0.name}', user_path'{0.user_path}')>".format(self)