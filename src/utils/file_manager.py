import asyncio
import functools
import os
from typing import List
from pathlib import Path
import shutil
import glob

from loguru import logger

from ..config import BASE_PATH
from .mixins import ContextInstanceMixin


__all__ = ("FileManager", "wrap")

from ..models.base import make_request


def wrap(func):
    @functools.wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class FileManager(ContextInstanceMixin):
    def __init__(self, loop=None):
        """
        :param loop: need for execute blocking IO
        """
        if loop is None:
            self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._loop: asyncio.AbstractEventLoop = loop

    @staticmethod
    def _create_file(name: str, user_path: str, type_: str = "py") -> None:
        """
        Private func

        it uses for creating file, but its blocking io
        and this func run in executor
        calling for create file

        :param name:
        :param user_path:
        :param type_:
        :return:
        """
        if not name:
            return
        with open(f"{user_path}/{name}.{type_}", "w"):
            pass

    @staticmethod
    def list_files(user) -> List[str]:
        """
        Get user path based on user model
        no checks

        :param user:
        :return:
        """
        file_path = user.user_path

        files = os.listdir(file_path)
        return files

    @staticmethod
    @wrap
    def create_guild_folder(guild_id: int):
        """
        create guild folder, and when bot joins guild folder will create

        :param guild_id:
        :return:
        """
        bs_p = Path(__file__).parent.parent.parent
        guild_path = fr"{bs_p}\{BASE_PATH}\guild_{guild_id}"

        p = fr"{bs_p}\{BASE_PATH}"
        if os.path.exists(p):
            pass
        else:
            os.mkdir(p)

        if os.path.exists(guild_path):
            return

        os.mkdir(guild_path)

    @staticmethod
    @wrap
    def create_user_folder(user_path: str, user_id: int):
        """
        Private function
        get user_path and create user folder in guild_{guild_id}/ path

        :param user_path:
        :param user_id:
        :return:
        """
        user_path = user_path
        user_path_len = len(user_path)

        path_to_slice = len(f"user_{user_id}")
        path_final = user_path_len - path_to_slice

        if not os.path.exists(user_path[0:path_final]):
            os.mkdir(user_path[0:path_final])
        if os.path.exists(user_path):
            return

        os.mkdir(user_path)

    @staticmethod
    async def delete_all_guild_files(guild_id: int = None):
        """
        Deleting all files from working directory!
        if DELETE_ALL_FILES is true that delete all files from file/ directory
        :return:
        """
        if not guild_id:
            list_dirs = glob.glob(fr"{BASE_PATH}\*")
        else:
            list_dirs = glob.glob(fr"{BASE_PATH}\guild_{guild_id}")
        successful = []
        unsuccessful = {}
        for dirs in list_dirs:
            try:
                shutil.rmtree(dirs)
                successful.append(dirs)
            except (FileExistsError, FileNotFoundError, NotADirectoryError) as exc:
                unsuccessful[dirs] = exc

    @staticmethod
    @wrap
    def remove_user_folder(user):
        """
        Removes user folder, with all files directory

        :param user:
        :return:
        """
        user_path = user.user_path

        if not user_path:
            return

        list_files = os.listdir(user_path)
        for file in list_files:
            os.remove(f"{user_path}/{file}")
        shutil.rmtree(user_path)
        user.delete()

    @staticmethod
    @wrap
    def get_line(line: int, user):
        """
        get user path and select this, and open it

        :param line:
        :param user:
        :return:
        """
        user_file = user.current_file
        with open(user_file, "r") as f:
            data = f.readlines()

        return data[line]

    @staticmethod
    @wrap
    def change_line(user, line: int, to_change: str):
        with open(user.current_file, "w") as file:
            file.seek(line)
            file.write(to_change)

    async def change_file_name(self, user, file: str, to_change: str):
        await self._loop.run_in_executor(None, os.rename, fr"{user.user_path}\{file}", fr"{user.user_path}\{to_change}")

    async def create_file(self, file_name: str, user_path: str, type_: str = None):
        """
        Create file based on user path
        and user can set type of file
        if not type then creates .py file

        :param file_name:
        :param user_path:
        :param type_:
        :return:
        """
        if not file_name:
            return
        if not os.path.exists(f"{user_path}/{file_name}"):
            print(f"{user_path=} {file_name=}")
            loop = asyncio.get_running_loop()
            type = type_ if type_ else "py"
            try:
                await loop.run_in_executor(None, self._create_file, file_name, user_path, type)
            except OSError as exc:
                logger.error(exc)
        else:
            return

    async def remove_file(self, filename: str, user):
        """
        need user, and filename argument for delete file
        run os.remove blocking io in executor

        :param filename:
        :param user:
        :return:
        """
        user_path = user.user_path

        if not filename:
            return
        await self._loop.run_in_executor(None, os.remove, f"{user_path}/{filename}")

    async def read_file(self, filename: str, user_path: str):


    @wrap
    def open_file(self, filename: str, user_path: str, user_id: int):
        """
        Opens file, need a filename and User
        set user.current_file to filename

        :param user_path:
        :param filename:
        :param user_id:
        :return:
        """
        fp = f"{user_path}/{filename}"

        with open(fp, "r") as f:
            lines = f.readlines()
            return "\n".join(lines) if lines else "File is Empty..."

    @wrap
    def write_to_file(self, text: str, user):
        """
        checks for user current file if not current file
        function dissmiss it.
        in stock user.current_file is main.py, starter script

        :param text:
        :param user:
        :return:
        """
        current_file = user.current_file

        if not self.list_files:
            return

        with open(current_file, "w") as file:
            file.write(text)

    @wrap
    def search_in_file(self, query: str, current_file: str):
        with open(current_file, 'r') as f:
            return [m if m in [f'{query}\n', query] else None for m in f.readlines()]
