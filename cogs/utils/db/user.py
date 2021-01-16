from .db import db, TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    user_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(256))
    current_file = db.Column(db.String(256))
    user_path = db.Column(db.String(256))
    is_owner = db.Column(db.Boolean)
    cursor = db.Column(db.Integer, default=0)
