import asyncio

from loguru import logger

from bot import Bot


def main():
    loop = asyncio.get_event_loop()

    bot = Bot(loop)
    try:
        loop.run_until_complete(bot.run_bot())
    except KeyboardInterrupt:
        logger.info("GoodBye")
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()
