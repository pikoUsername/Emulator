from loguru import logger

from .db import User


async def set_owner(user_id: int, remove: bool) -> bool:
    user = await User.query.where(User.user_id == user_id).gino.first()
    if not user:
        logger.info("User Not Exists")
        raise TypeError("User Not Exists")

    await user.update(is_owner=not remove).apply()

    return True
