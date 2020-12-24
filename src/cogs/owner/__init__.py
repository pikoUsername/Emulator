import asyncio
import sys
from typing import List
import os
from math import ceil

import discord
from discord.ext import commands

from data.base_cfg import LOGS_BASE_PATH

class OwnerCommands(commands.Cog):
    """ Only for owners """
    def __init__(self, bot):
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
    @commands.is_owner()
    async def load_extension(self, ctx: commands.Context, *, cogs: str):
        try:
            for cog in cogs:
                self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command()
    @commands.is_owner()
    async def load_custom_extension(self, ctx: commands.Context, *, file: str):
        user = await self.bot.uapi.get_user_by_id(ctx.author.id)

        file_path = f"{user.user_path}/{file}"

        if not os.path.exists(file_path):
            return await ctx.send("File NOT EXISTS")
        to_load_extension = file_path.replace("/", ".")

        try:
            self.bot.load_extension(to_load_extension)
        except Exception as e:
            return await ctx.send(f"Failed to load. **ERROR: **\n```{e}```")

    @commands.command()
    @commands.is_owner()
    async def unload_cogs(self, ctx: commands.Context, cog: str):
        failed = []
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            return await ctx.send(e)

        return await ctx.message.add_reaction("✅")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_guild_folder(self, ctx: commands.Context):

        if not self.bot.drop_after_restart:
            await ctx.send(embed=discord.Embed(
                title=f"Error, {self.bot.X_EMOJI}",
                description="Deleting guild files is turned OFF, so you cant delete them!"
            ))
            return

        try:
            await self.bot.fm.delete_all_guild_files()
        except Exception:
            return await ctx.send("Error for removing guild folder!")
        else:
            await ctx.send(embed=discord.Embed(
                title="Success :white_check_mark:",
                description="Now your discord servers folder was removed, now your members leave!",
            ).set_footer(text=f"Removed By {ctx.author.mention}", icon_url=ctx.author.avatar_url)
            )
        try:
            await ctx.send("@everyone All yours files was removed! Now leave from guild")
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

    @staticmethod
    def parting(xs, parts):
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

        if len(text) <= 2048:
            return await ctx.author.send(embed=discord.Embed(title="Whole Log", description=f"```{text}```"))

        try:
            whole_log = await self.bot.loop.run_in_executor(None, self.parting, text, 5)
            for peace in whole_log:
                await ctx.author.send(peace)
                await asyncio.sleep(0.2)
        except Exception:
            return await ctx.author.send(text)

    @commands.command()
    @commands.is_owner()
    async def reload_cogs(self, ctx: commands.Context):
        """ Reload all Cogs """

        successful = []
        unsuccessful = {}
        exts = [x for x in self.bot.extensions.keys()]
        current_cogs = [[exts[index], cog] for index, cog in enumerate(self.bot.cogs.values())]
        for cog_name, cog in current_cogs:
            try:
                self.bot.reload_extension(cog_name)
                if hasattr(cog, "show_name"):
                    successful.append(f"`{cog_name[5:]}`")
            except Exception as e:
                unsuccessful[cog_name] = f"{type(e).__name__} - {e}"

        if unsuccessful:
            fmt = ["I caught some errors:"]
            for key, value in unsuccessful.items():
                error = f"{key} - {value}"
                fmt.append(error)

            await ctx.send("\n".join(fmt))

        await ctx.send(f"Successfully reloaded:\n{', '.join(successful)}")

def setup(bot):
    bot.add_cog(OwnerCommands(bot))