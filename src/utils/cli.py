import asyncio
import functools

from loguru import logger
import click

from ..loader import Bot
from .file_manager import FileManager

try:
    import aiohttp_autoreload
except ImportError:
    aiohttp_autoreload = None


__all__ = ("cli", "polling", "superuser")


@click.group()
def cli():
    from . import log
    log.setup()


def auto_reload_mixin(func):
    @click.option(
        "--autoreload", is_flag=True, default=False, help="Reload application on file changes"
    )
    @functools.wraps(func)
    def wrapper(autoreload: bool, *args, **kwargs):
        if autoreload and aiohttp_autoreload:
            logger.warning(
                "Application started in live-reload mode. Please disable it in production!"
            )
            aiohttp_autoreload.start()
        elif autoreload and not aiohttp_autoreload:
            click.echo("`aiohttp_autoreload` is not installed.", err=True)
        return func(*args, **kwargs)

    return wrapper


@cli.command()
@auto_reload_mixin
def polling():
    fm = FileManager()
    FileManager.set_current(fm)
    bot = Bot(fm=fm)
    loop = asyncio.get_event_loop()
    run = loop.run_until_complete

    try:
        run(bot.run_itself())
    finally:
        run(bot.close_all())


@cli.command()
@click.argument("user_id", type=int)
@click.option("--remove", "--rm", is_flag=True, default=False, help="Remove superuser rights")
def superuser(user_id: int, remove: bool):
    from src.utils.set_owner import create_owner_user
    loop = asyncio.get_event_loop()
    run = loop.run_until_complete
    try:
        result = run(create_owner_user(user_id, remove))
    except Exception as e:
        logger.exception("Failed to create superuser: {e}", e=e)
        result = None

    if not result:
        exit(1)
