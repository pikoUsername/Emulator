from discord.ext import commands
import discord

from src.db.guild import AVALIABLE_LANGUAGES, GuildAPI

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(Adminstrator=True)
    async def change_lang(self, ctx: commands.Context, language: str):
        for keys in AVALIABLE_LANGUAGES.keys():
            if not keys in language:
                return await ctx.send("Not available language")
            continue

        gapi = GuildAPI()
        guild = await gapi.get_guild(ctx.guild.id)

        try:
            await guild.update(language=language).apply()
            await ctx.send(f"Command Not work, YET")
        except Exception as e:
            return await ctx.send("Fail to change guild language, try again")