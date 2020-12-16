from discord.ext import commands

class DiscordInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["?"])
    async def info(self, ctx: commands.Context):
        return await ctx.send("Github - https://github.com/pikoUsername/Emulator")

def setup(bot):
    bot.add_cog(DiscordInfo(bot))
