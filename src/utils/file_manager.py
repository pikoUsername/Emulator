import asyncio
import os
from typing import List
from glob import glob

from src.db.user import User
from src.db.guild import Guild

from data.base_cfg import BASE_PATH

class FileManager:
    def __init__(self, loop=None):
        """
        :param loop: need for execute blocking IO
        """
        if loop is None:
            self._loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self._loop: asyncio.AbstractEventLoop = loop

    @staticmethod
    def _create_file(name: str, user: User, type_: str = "py") -> None:
        """
        Private func

        it uses for creating file, but its blocking io
        and this func run in executor
        calling for create file

        :param name:
        :param user:
        :param type_:
        :return:
        """
        if not name:
            return
        with open(f"{user.user_path}/{name}.{type_}", "w"):
            pass

    @staticmethod
    def list_files(user: User) -> List:
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
    def _create_guild_folder(guild: Guild):
        """
        Private function
        |staticmethod|

        create guild folder, and when bot joins guild folder will create

        :param guild:
        :return:
        """
        guild_path = fr"{BASE_PATH}\guild_{guild.guild_id}"

        if os.path.exists(guild_path):
            return

        try:
            os.mkdir(guild_path)
        except Exception as e:
            raise e

    @staticmethod
    def _create_user_folder(user: User):
        """
        Private function
        get user_path and create user folder in guild_{guild_id}/ path

        :param user:
        :return:
        """
        user_path = user.user_path
        user_path_len = len(user_path)

        path_to_slice = len(user.username)
        path_final = user_path_len - path_to_slice

        if not os.path.exists(user_path[0:path_final]):
            os.mkdir(user_path[0:path_final])
        if os.path.exists(user_path):
            return

        os.mkdir(user_path)

    @staticmethod
    def delete_all_working_files():
        """
        Deleting all files from working directory!
        if DELETE_ALL_FILES is true that delete all files from file/ directory
        :return:
        """
        to_remove = glob(f"{BASE_PATH}/*")

        for files in to_remove:
            try:
                os.remove(files)
            except PermissionError:
                pass


    @staticmethod
    def _get_line(line: int, user: User):
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

    async def create_file(self, file_name: str, user: User, type_: str="py"):
        """
        Create file based on user path
        and user can set type of file
        if not type then creates .py file

        :param file_name:
        :param user:
        :param type_:
        :return:
        """
        if not file_name:
            return
        if not os.path.exists(f"{user.current_path}/{file_name}"):
            await self._loop.run_in_executor(None, self._create_file, file_name, type_)
        else:
            return

    async def remove_file(self, filename: str, user: User):
        """
        need user, and filename argument for delete file
        run os.remove blocking io in executor

        :param filename:
        :param user:
        :return:
        """
        user_path = user.user_path

        if not os.path.exists(f"{user_path}/{filename}"):
            return
        if not filename:
            return
        await self._loop.run_in_executor(None, os.remove, filename)


    async def open_file(self, filename: str, user: User):
        """
        Opens file, need a filename and User
        set user.current_file to filename

        :param user:
        :param filename:
        :return:
        """
        pass

    def _write_to_file(self, text: str, user: User):
        """
        Private function

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

    async def write_to_file(self, text: str, user: User):
        """
        run in executor _write_to_file function
        need text and user arguments

        :param user:
        :param text:
        :return:
        """
        if not text:
            return

        loop = self._loop
        await loop.run_in_executor(None, self._write_to_file, text, user)


    async def create_guild_folder(self, guild: Guild):
        try:
            await self._loop.run_in_executor(None, self._create_guild_folder, guild)
        except Exception as e:
            raise e

    async def create_user_folder(self, user: User):
        """
        try to run _create_user_folder

        :param user:
        :return:
        """
        try:
            await self._loop.run_in_executor(None, self._create_user_folder, user)
        except Exception as e:
            raise e

    async def get_line(self, line: int, user: User):
        try:
            await self._loop.run_in_executor(None, self._get_line, line, user)
        except Exception as e:
            raise e