import asyncio
import sys

import discord
from discord.ext import commands

class OwnerCommands(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reboot(self, ctx: commands.Context):
        """
        Reboot the bot

        :param ctx:
        :return:
        """
        await ctx.send("Rebooting...")
        await asyncio.sleep(1)
        sys.exit(0)

    @commands.command()
    @commands.is_owner()
    async def dm_send(self, ctx: commands.Context, user_id: int, *, message: str):
        """ DM the user of your choice """
        user = self.bot.get_user(user_id)
        if not user:
            return await ctx.send(f"Could not find any UserID matching **{user_id}**")

        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.command()
    @commands.is_owner()
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))