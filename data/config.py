from typing import Optional
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LOGS_BASE_PATH = str(Path(__name__).parent.parent / "logs")

def dstr(key: str, default: Optional[str] = None):
    return str(os.getenv(key, default))

def dint(key: str, default: Optional[int] = 0):
    return os.getenv(key, default)

def dbool(key: str, default: Optional[bool]=True):
    return os.getenv(key, default)
