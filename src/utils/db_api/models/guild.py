# here guild register
from .base import BaseModel, db

class Guild(BaseModel):
    query: db.sql.Select

    id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    guild_id = db.Column(db.Integer)
    guild_name = db.Column(db.String(200))
