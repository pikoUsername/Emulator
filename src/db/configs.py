
from .base import db, BaseModel


class Config(BaseModel):
    """
    using by user, guild model
    this models descibes:
    id: int
    name: str with it get configs
    settings: **kwargs
    """
    __tablename__ = 'configs'

    query: db.sql.Select

    id = db.Column(db.Integer, db.Sequence("config_id_seq"), primary_key=True)
    name = db.Column(db.String(100))


