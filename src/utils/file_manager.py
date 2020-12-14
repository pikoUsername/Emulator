import asyncio
import os

from src.db.user import User

class FileManager:
    def __init__(self, user: User, path: str=None):
        self.user = user
        if not path:
            self.path = user.get_current().user_path
        else:
            self.path = path
        self._loop = asyncio.get_event_loop()

    @property
    def current_path(self):
        return self.path

    async def create_file(self, file_name: str, type_: str="py"):
        if not file_name:
            return
        if not os.path.exists(f"{self.current_path}/{file_name}"):
            await self._loop.run_in_executor(None, self._create_file, file_name, type_)
        else:
            return

    def _create_file(self, name: str, type_: str="py") -> None:
        if not name:
            return
        with open(f"{self.path}/{name}.{type_}", "w"):
            pass

    async def remove_file(self, filename: str):
        user = self.user
        user_path = user.user_path

        if not os.path.exists(f"{user_path}/{filename}"):
            return
        if not filename:
            return
        await self._loop.run_in_executor(None, os.remove, filename)


    async def open_file(self, filename: str):
        pass

    async def list_files(self):
        file_path = self.path
