from loguru import logger

from src.models import User


async def create_owner_user(user_id: int, remove: bool) -> bool:
    user = await User.query.where(User.user_id == user_id).gino.first()
    if not user:
        logger.error("No User")
        raise TypeError("No User to set")

    logger.info(
        "Loaded user {user}.",
        user=user.user_id,
    )
    await user.update(is_owner=not remove).apply()
    if remove:
        logger.warning("User {user} now IS NOT superuser", user=user_id)
    else:
        logger.warning("User {user} now IS superuser", user=user_id)
    return True
