class FileManager:
    def __init__(self, loop, bind):
        self.loop = loop
        self.bind = bind

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
