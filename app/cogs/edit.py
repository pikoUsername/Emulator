from discord.ext import commands

from .utils.file_manager import change_file


class Edit(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def edit_l(self, ctx, line: int, *, w_text: str):
        """Edit Selected Line"""



def setup(bot):
    bot.add_cog(Edit(bot))
