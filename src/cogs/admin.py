import typing

from discord.ext import commands
import discord


class AdminCommands(commands.Cog):
    __slots__ = "bot",
    """ Here Admin commands, and mod commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["rm-ufull"])
    @commands.has_permissions(administrator=True)
    async def remove_user(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """ Deletes user from bot, not a discord Guild """
        if ctx.author.id == member.id:
            return

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
                description="User folder was removed, and table too",))
            await member.send(f"You now in {ctx.guild.guild_name}, was removed forever, reason: {reason}")
        except Exception:
            await ctx.send(embed=discord.Embed(title=f"failed {self.bot.X_EMOJI}",
                           description="Failed to remove user model, and folder! maybe permission error"))

    @commands.command()
    @commands.is_owner()
    async def set_prefix(self, ctx: commands.Context, prefix: str):
        result = self.bot.set_prefix(ctx.guild, prefix)

        if not result:
            return await ctx.send("Prefix Len is More than 10 letters")
        return await ctx.send("Success")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_guild_folder(self, ctx: commands.Context):

        if not hasattr(self.bot, 'drop_after_restart'):
            await ctx.send(embed=discord.Embed(
                title=f"Error, {self.bot.X_EMOJI}",
                description="Deleting guild files is turned OFF, so you cant delete them!"
            ))
            return

        try:
            await self.bot.fm.delete_all_guild_files(ctx.guild.id)
        except Exception as e:
            raise commands.CommandInvokeError(e)
        else:
            await ctx.send(embed=discord.Embed(
                title=f"Success {self.bot.APPLY_EMOJI}",
                description="Now your discord servers folder was removed, now your members leave!",
            ).set_footer(text=f"Removed By {ctx.author.mention}", icon_url=ctx.author.avatar_url)
            )
        try:
            await ctx.send("@everyone All yours files was removed! Now leave from guild")
        except commands.BotMissingPermissions:
            pass


def setup(bot):
    bot.add_cog(AdminCommands(bot))
