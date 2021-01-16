import os
import asyncio
import functools


def wrap(func):
    @functools.wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


stat = wrap(os.stat)
rename = wrap(os.rename)
remove = wrap(os.remove)
mkdir = wrap(os.mkdir)
rmdir = wrap(os.rmdir)


class FileManager:
    def __init__(self, loop):
        self.loop = loop

    async def create_user_folder(self, user_id: int):
        pass

    async def exit_from_file(self, user_id: int):
        pass

    async def write_file(self, user_id: int, lines: str):
        pass

    async def read_file(self, user_id: int):
        pass

    async def delete_guild_folder(self, guild_id: int):
        pass

    async def delete_user_folder(self, user_id: int, guild_id: int):
        pass
