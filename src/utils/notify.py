from loguru import logger

from ..models import UserApi


async def notify_all_owners(bot, text: str) -> None:
    logger.info("Notifying All Owners")
    all_owners = await UserApi.get_all_owners()
    for owner in all_owners:
        try:
            await bot.spammer.say_to_user(bot, owner.user_id, content=text)
        except AttributeError:
            pass
        except TypeError as exc:
            logger.error(exc)
            break
