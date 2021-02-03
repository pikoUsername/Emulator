from pathlib import Path, PurePath
from typing import Union, Optional

from ..config import BASE_PATH


def create_path(guild_id: int, user_id: int) -> Optional[PurePath]:
    return Path(fr"{BASE_PATH}\guild_{guild_id}\user_{user_id}")
