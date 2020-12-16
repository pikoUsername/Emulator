import asyncio
import os
from typing import List

from src.db.user import User
from src.db.guild import Guild

from data.base_cfg import BASE_PATH

class FileManager:
    def __init__(self, loop=None):
        if loop is None:
            self.loop = asyncio.get_event_loop()
        self._loop = loop

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

    def _create_file(self, name: str, user: User, type_: str="py") -> None:
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

    def list_files(self, user: User) -> List:
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
        |staticmethod|

        create guild folder, and when bot joins guild folder will create

        :param guild:
        :return:
        """
        guild_path = fr"\guild_{guild.guild_id}"

        if not guild_path:
            return
        elif os.path.exists(guild_path):
            return

        os.mkdir(guild_path)

    async def create_guild_folder(self, guild: Guild):
        if not guild:
            return

        await self._loop.run_in_executor(None, self._create_guild_folder, guild)

    async def _create_user_folder(self, user: User):
        """
        get user_path and

        :param user:
        :return:
        """

        guild_path = f"guild_{guild.guild_id}"

    async def create_user_folder(self, user: User):
        await self.loop.run_in_executor(None, self._create_user_folder())