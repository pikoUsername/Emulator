import asyncio

from loguru import logger

from src.loader import Bot

def main():
    run_bot()

def run_bot():
    bot = Bot()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.run_itself())
    except Exception as e:
        logger.exception(f"ERROR: {e}")
    except KeyboardInterrupt:
        logger.info("goodbye")
    finally:
        try:
            loop.run_until_complete(bot.logout())
        except asyncio.TimeoutError:
            pass

if __name__ == '__main__':
    logger.info("activating main()")
    main()
