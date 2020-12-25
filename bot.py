import asyncio

from loguru import logger

from src.loader import Bot

def main():
    bot = Bot()
    loop = asyncio.get_event_loop()
    run = loop.run_until_complete

    try:
        run((bot.run_itself()))
    except Exception as e:
        logger.exception(f"ERROR: {e}")
    except KeyboardInterrupt:
        logger.info("goodbye")
    finally:
        try:
            run((bot.logout()))
        except asyncio.TimeoutError:
            pass

if __name__ == '__main__':
    logger.info("activating main()")
    main()
