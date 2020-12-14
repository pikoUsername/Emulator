
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
    prefix = db.Columb(db.String(10))

    def __repr__(self):
        return "<configs id='{0.id}', prefix='{0.prefix}'>".format(self)
