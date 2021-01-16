import asyncio
import functools
import os
import shutil
from typing import List
import glob

from discord.ext import commands
from loguru import logger

from .db import User, Guild


def wrap(func):
    @functools.wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class FileManager:
    def __init__(self, loop, bind, data):
        self.loop = loop
        self.bind = bind
        self.data = data

    @staticmethod
    @wrap
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
        with open(fr"{user.user_path}\{name}.{type_}", "w"):
            pass

    @staticmethod
    @wrap
    def list_files(user: User) -> List[str]:
        """
        Get user path based on user model
        no checks

        :param user:
        :return:
        """
        files = os.listdir(user.user_path)
        return files

    @wrap
    def _create_guild_folder(self, guild: Guild):
        """
        create guild folder, and when bot joins guild folder will create

        :param guild:
        :return:
        """
        guild_path = fr"{self.data['bot']['BASE_PATH']}\guild_{guild.guild_id}"

        if os.path.exists(guild_path):
            return

        os.mkdir(guild_path)

    async def create_guild_folder(self, guild_id: int):
        guild = await Guild.query.where(Guild.guild_id == guild_id).gino.first()

        try:
            await self._create_guild_folder(guild)
        except Exception as e:
            logger.error(e)
            raise e

    @staticmethod
    @wrap
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

    @wrap
    def delete_all_guild_files(self, g_id: int = None):
        """
        Deleting all files from working directory!
        if DELETE_ALL_FILES is true that delete all files from file/ directory
        :return:
        """
        base_path = self.data['bot']['BASE_PATH']
        if not g_id:
            list_dirs = glob.glob(fr"{base_path}\*")
        else:
            list_dirs = glob.glob(fr"{base_path}\guild_{g_id}")

        for dirs in list_dirs:
            try:
                shutil.rmtree(dirs)
            except Exception:
                pass

    @staticmethod
    @wrap
    def _delete_user_folder(user: User):
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
    def _read_file(user: User, file: str = None):
        """Open current file or chosed"""
        path = user.current_file
        if file:
            path = fr"{user.user_path}\{file}"

        with open(path, "r") as data:
            return "\n".join(data.readlines())

    @staticmethod
    @wrap
    def _write_file(user: User, lines: str, file: str):
        path = user.current_file
        if file:
            path = fr"{user.user_path}\{file}"

        with open(path, "r") as data:
            saved_file = data.readlines()

        with open(path, "w") as file:
            for line in file:
                if line == user.line_cursor:
                    line = lines
            for l in lines:
                pass  # no yet

    @staticmethod
    def _change_line(user: User, line: int, to_change: str):
        with open(user.current_file, "w") as file:
            file.seek(line)
            file.write(to_change)

    async def create_user_folder(self, user_id: int):
        user = await User.query.where(User.user_id == user_id).gino.first()

        await self.loop.run_in_executor(self._create_user_folder, user)

    @staticmethod
    async def exit_from_file(user_id: int):
        user = await User.query.where(User.user_id == user_id).gino.first()

        try:
            m = user.user_path
            await user.update(current_file=m).apply()
        except AttributeError:
            return False
        else:
            return True

    async def write_file(self, user_id: int, lines: str, file: str=None):
        user = await User.query.where(User.user_id == user_id).gino.first()
        try:
            await self._write_file(user, lines, file)
        except FileNotFoundError:
            return False
        else:
            return True

    async def read_file(self, user_id: int, file: str = None):
        user = await User.query.where(User.user_id == user_id).gino.first()

        await self.read_file(user.user_path, file)

    async def delete_user_folder(self, u_id: int):
        user = await User.query.where(User.user_id == u_id).gino.first()

        await self._delete_user_folder(user)
