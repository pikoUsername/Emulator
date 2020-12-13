from .base import db, BaseModel

class File(BaseModel):
    """
    describes:
    id: int
    path: int
    file: str
    line: int
    only_read: bool - if file in others directory, or a big files
    """
    __tablename__ = 'files'

