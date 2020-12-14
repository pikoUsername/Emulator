import asyncio

from loguru import logger

from src.loader import Bot
from src.utils import log
from src.db.base import create_db
from data.config import dstr

async def main():
    await run_bot()

async def run_bot() -> None:
    await create_db()

    bot = Bot(
        command_prefix=dstr("PREFIX"),
        help_attrs=dict(hidden=True), pm_help=None,
    )

    try:
        import uvloop
    except ImportError:
        pass
    finally:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    try:
        await bot.run_itself()
    except Exception as e:
        logger.exception(f"ERROR: {e}")
    except KeyboardInterrupt:
        logger.info("goodbye")
    finally:
        await bot.logout()

if __name__ == '__main__':
    logger.info("activating main()")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
