from pathlib import Path

from .config import dstr, dint

BASE_PATH = str(Path(__name__).parent.parent / "files")

POSTGRES_NAME = dstr("DB_NAME")
POSTGRES_HOST = dstr("DB_HOST")
POSTGRES_PORT = dint("DB_PORT")
POSTGRES_USER = dstr("DB_USER")
POSTGRES_PASS = dstr("DB_PASS")

POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"