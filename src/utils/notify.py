from discord.ext.commands import AutoShardedBot
from loguru import logger

from ..models import UserApi
from .spammer import say_to_user


async def notify_all_owners(bot: AutoShardedBot, text: str) -> None:
    logger.info("Notifying All Owners")
    all_owners = await UserApi.get_all_owners()
    for owner in all_owners:
        try:
            await say_to_user(bot, owner.user_id, text)
        except AttributeError:
            pass
        except TypeError as exc:
            logger.error(exc)
            break