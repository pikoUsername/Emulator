import asyncio
import os

from src.db.user import User

class FileManager:
    def __init__(self, loop=None):
        if loop is None:
            self.loop = asyncio.get_event_loop()
        self._loop = loop

    async def create_file(self, file_name: str, user: User, type_: str="py"):
        if not file_name:
            return
        if not os.path.exists(f"{user.current_path}/{file_name}"):
            await self._loop.run_in_executor(None, self._create_file, file_name, type_)
        else:
            return

    def _create_file(self, name: str, user: User, type_: str="py") -> None:
        if not name:
            return
        with open(f"{user.user_path}/{name}.{type_}", "w"):
            pass

    async def remove_file(self, filename: str, user: User):
        user_path = user.user_path

        if not os.path.exists(f"{user_path}/{filename}"):
            return
        if not filename:
            return
        await self._loop.run_in_executor(None, os.remove, filename)


    async def open_file(self, filename: str):
        pass

    def _write_to_file(self, text: str, user: User):
        current_file = user.current_file

        if not self.list_files:
            return

        with open(current_file, "w") as file:
            file.write(text)

    async def write_to_file(self, text: str):
        if not text:
            return

        loop = self._loop
        loop.run_in_executor(None, self._write_to_file, text)

    def list_files(self, user: User):
        file_path = user.user_path

        files = os.listdir(file_path)
        if not files:
            return
        return files