from typing import Optional, Union
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

LOGS_BASE_PATH = str(Path(__name__).parent.parent / "logs")


def dstr(key: str, default: Optional[str] = None):
    return str(os.getenv(key, default))


def dint(key: str, default: Optional[int] = 0):
    return os.getenv(key, default)


def dbool(key: str, default: Optional[bool] = True):
    return os.getenv(key, default)


def dlist(key: str, default: Union[str, int] = None):
    return [os.getenv(key, default)]


BASE_PATH = str(Path(__name__).parent.parent / "files")

POSTGRES_NAME = dstr("DB_NAME")
POSTGRES_HOST = dstr("DB_HOST")
POSTGRES_PORT = dint("DB_PORT")
POSTGRES_USER = dstr("DB_USER")
POSTGRES_PASS = dstr("DB_PASS")


WEB_HOOK_URL = dstr("WEB_HOOK_URL")
TOKEN = dstr("BOT_TOKEN")
PREFIX = os.getenv("PREFIX")
description = dstr("description", None)


ERROR_CHANNEL = os.getenv("ERROR_CHANNEL")
START_CHANNEL = os.getenv("START_CHANNEL")


DROP_AFTER_RESTART = os.getenv("DROP_AFTER_RESTART")
LOG_LEVEL = os.getenv("LOG_LEVEL")


POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
