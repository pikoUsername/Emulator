from .db import db, TimedBaseModel


class Guild(TimedBaseModel):
    __tablename__ = 'guilds'

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    guild_id = db.Column(db.BigInteger)
    name = db.Column(db.String(255))
