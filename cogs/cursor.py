from discord.ext import commands


class Cursor(commands.Cog):
    __slots__ = ("bot",)

    def __init__(self, bot):
        self.bot = bot

    async def change_cursor_position(self, user_id: int, line: int):
        pass

    @commands.command(name="to")
    async def change_cursor(self, ctx: commands.Context, line_number: int):
        pass

    @commands.command(aliases="G")
    async def to_start_line(self, ctx: commands.Context):
        """Cursor goes to Start Of File"""
        pass

    @commands.command(name="gg")
    async def to_end_file(self, ctx: commands.Context):
        """Cursor Go to End Of File"""
        pass


def setup(bot):
    bot.add_cog(Cursor(bot))
