from sqlalchemy import ForeignKey
# here guild register
from .base import BaseModel, db


class Guild(BaseModel):
    __tablename__ = 'guilds'

    query: db.sql.Select

    id = db.Column(db.Integer, db.Sequence("user_id_seq"), primary_key=True)
    guild_id = db.Column(db.Integer)
    guild_name = db.Column(db.String(200))
    config = ForeignKey('Config')

    def __repr__(self):
        return "<Guild(id='{0.id}', guild_id='{0.guild_id}', guild_name='{0.guild_name}'".format(self)
