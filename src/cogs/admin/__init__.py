from discord.ext import commands
import discord

from src.db.guild import GuildAPI

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def change_lang(self, ctx: commands.Context, language: str):
        AVALIABLE_LANGUAGES = {"Lol": "No"}
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

    @commands.command(aliases=["rm-ufull"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove_user(self, ctx: commands.Context, member: discord.Member, *, reason: str=None):
        """ Deletes user from bot, not a discord Guild """
        if ctx.author.id == memeber.id: 
        	await ctx.send(embed=discord.Embed(
        		title=f"ERROR {self.bot.X_EMOJI}",
        		description="You cant remove yourself!"
        	))

        user = await self.bot.uapi.get_user_by_id(member.id)

        if not user:
            await ctx.send(embed=discord.Embed(
                title="This user Not exists",
                description="You cant remove user, whose not authed in bot",
            ))
            return

        try:
            await user.delete()
            await self.bot.fm.remove_user_folder(user)
            await ctx.send(embed=discord.Embed(
                title=f"success {self.bot.APPLY_EMOJI}",
                description="User folder was removed, and table too",
            ))
            await member.send(f"You now in {ctx.guild.guild_name}, was removed forever, reason: {reason}")
        except Exception:
            await ctx.send(embed=discord.Embed(
                title=f"failed {self.bot.X_EMOJI}",
                description="Failed to remove user model, and folder! maybe permission error"
            ))

def setup(bot):
    bot.add_cog(AdminCommands(bot))