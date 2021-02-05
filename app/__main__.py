import asyncio

from app.bot import Bot


def main():
    loop = asyncio.get_event_loop()
    bot = Bot()

    loop.run_until_complete(bot.run_bot())


if __name__ == "__main__":
    main()
