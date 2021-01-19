import asyncio
import os
from typing import List
import shutil
import glob

from discord.ext import commands

from src.models import Guild, User
from data.config import BASE_PATH


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

    async def delete_all_guild_files(self, guild_id: int = None):
        await self._loop.run_in_executor(None, self._delete_all_guild_files, guild_id)

    @staticmethod
    def _delete_all_guild_files(guild_id: int = None):
        """
        Deleting all files from working directory!
        if DELETE_ALL_FILES is true that delete all files from file/ directory
        :return:
        """
        if not guild_id:
            list_dirs = glob.glob(fr"{BASE_PATH}\*")
        else:
            list_dirs = glob.glob(fr"{BASE_PATH}\guild_{guild_id}")

        for dirs in list_dirs:
            try:
                shutil.rmtree(dirs)
            except Exception:
                pass

    @staticmethod
    def _remove_user_folder(user: User):
        """
        Removes user folder, with all files directory

        :param user:
        :return:
        """
        user_path = user.user_path

        if not user_path:
            return

        list_files = os.listdir(user_path)
        try:
            for file in list_files:
                os.remove(f"{user_path}/{file}")
            shutil.rmtree(user_path)
        except Exception:
            commands.CommandInvokeError("Failed to remove user dir")

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

    @staticmethod
    def _change_line(user: User, line: int, to_change: str):
        with open(user.current_file, "w") as file:
            file.seek(line)
            file.write(to_change)

    async def change_file_name(self, user: User, file: str, to_change: str):
        await self._loop.run_in_executor(None, os.rename, fr"{user.user_path}\{file}", fr"{user.user_path}\{to_change}")

    async def create_file(self, file_name: str, user: User, type_: str = "py"):
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
        if not os.path.exists(f"{user.user_path}/{file_name}"):
            await self._loop.run_in_executor(None, self._create_file, file_name, user, type_)
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

        if not filename:
            return
        await self._loop.run_in_executor(None, os.remove, f"{user_path}/{filename}")

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

    async def change_line(self, user: User, line: int, to_change: str = "\n"):
        try:
            await self._loop.run_in_executor(None, self._change_line, user, line, to_change)
        except Exception:
            raise commands.CommandInvokeError("Fail to change line")

    async def remove_user_folder(self, user: User):
        try:
            await self._loop.run_in_executor(None, self._remove_user_folder, user)
        except Exception as e:
            commands.CommandInvokeError(e)
