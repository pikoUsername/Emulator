import asyncio
import sys
from typing import List
import os
from math import ceil

import discord
from discord.ext import commands

from data.config import LOGS_BASE_PATH

class OwnerCommands(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reboot(self, ctx: commands.Context):
        """ Reboot the bot """
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
    @commands.has_permissions(administrator=True)
    async def remove_guild_folder(self, ctx: commands.Context):

        if not self.bot.DELETE_ALL_FILES:
            await ctx.send(embed=discord.Embed(
                title=f"Error, {self.bot.X_EMOJI}",
                description="Deleting guild files is turned OFF, so you cant delete them!"
            ))
            return

        try:
            await self.bot.fm.delete_all_guild_files()
        except Exception as e:
            return await ctx.send("Error for removing guild folder!")
        else:
            await ctx.send(embed=discord.Embed(
                title="Success :white_check_mark:",
                description="Now your discord servers folder was removed, now your members leave!",
            ).set_footer(text=f"Removed By {ctx.author.mention}", icon_url=ctx.author.avatar_url)
            )
        try:
            await ctx.send("@everyone All yours files was removed! Now leave from here")
        except PermissionError:
            pass

    @commands.command()
    @commands.is_owner()
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @property
    def last_log(self) -> List:
        """
        Get last log from /logs/ folder
        :return:
        """
        logs_list: List = os.listdir(LOGS_BASE_PATH)
        full_list = [os.path.join(LOGS_BASE_PATH, i) for i in logs_list]
        time_sorted_list: List = sorted(full_list, key=os.path.getmtime)

        if not time_sorted_list:
            return
        return time_sorted_list[-1]

    def parting(self, xs, parts):
        part_len = ceil(len(xs) / parts)
        return [xs[part_len * k:part_len * (k + 1)] for k in range(parts)]

    @commands.command()
    @commands.is_owner()
    async def get_logs(self, ctx: commands.Context):
        file_ = self.last_log
        file_name = ''.join(file_)

        try:
            with open(f"{file_name}", "r") as file:
                text = file.read()
        except Exception:
            return await ctx.send("Failed to load file!")

        if len(text) <= 4027:
            return await ctx.author.send(embed=discord.Embed(title="Whole Log", description=f"```{text}```"))

        try:
            whole_log = await self.bot.loop.run_in_executor(None, self.parting, text, 5)
            for peace in whole_log:
                await ctx.author.send(peace)
                await asyncio.sleep(0.2)
        except Exception:
            return await ctx.author.send(text)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))