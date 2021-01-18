import asyncio
import sys
from typing import List
import os
from math import ceil

import discord
from discord.ext import commands
from loguru import logger

from data.config import LOGS_BASE_PATH
from src.utils.set_owner import create_owner_user
from src.models.user import UserApi


class OwnerCommands(commands.Cog):
    __slots__ = ("bot",)
    """ Only for owners """
    def __init__(self, bot):
        self.bot = bot
        self.notes = []
        self.command_activated = 0

    async def cog_check(self, ctx: commands.Context):
        user = await UserApi.get_user_by_id(ctx.author.id)

        if not user:
            return await ctx.send("You Not Authed")

        elif not user.is_owner:
            raise commands.MissingPermissions("Missing Owner permissions")
        return True

    @commands.command()
    async def shutdown(self, ctx: commands.Context):
        """ Reboot the bot """
        await ctx.send("Shutdown...")
        sys.exit(0)

    @commands.command()
    async def dm_send(self, ctx: commands.Context, user_id: int, *, message: str):
        """ DM the user of your choice """
        user = self.bot.get_user(user_id)
        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.command()
    async def load_extension(self, ctx: commands.Context, *, cogs: str):
        """ Load Extension """
        try:
            for cog in cogs:
                self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.command()
    async def load_custom_extension(self, ctx: commands.Context, *, file: str):
        """ loade custom extesnion from user path """
        user = await UserApi.get_user_by_id(ctx.author.id)

        file_path = f"{user.user_path}/{file}"

        if not os.path.exists(file_path):
            return await ctx.send("File NOT EXISTS")
        to_load_extension = file_path.replace("/", ".")

        try:
            self.bot.load_extension(to_load_extension)
        except Exception as e:
            return await ctx.send(f"Failed to load. **ERROR: **\n```{e}```")

    @commands.command()
    async def unload_cogs(self, ctx: commands.Context, cog: str):
        """ Unload Selected Cogs """
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            return await ctx.send(str(e))

        return await ctx.message.add_reaction("✅")

    @commands.command()
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
    async def set_owner(self, ctx: commands.Context, user_id: int, remove: str=None):
        try:
            if remove == "-rm":
                await create_owner_user(user_id, remove=True)
            else:
                await create_owner_user(user_id, remove=False)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            raise e

    @commands.command()
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

    def change_error_channel(self, channel_id: int):
        err_channel = getattr(self.bot, 'error_channel', None)
        if not err_channel:
            logger.error("Error channel not exists")
            raise ValueError("Error channel not exists")

        new_err_channel = self.bot.get_channel(channel_id)
        setattr(self.bot, 'error_channel', new_err_channel)

    @commands.command()
    async def change_err_channel(self, ctx: commands.Context, channel_id: int):
        try:
            result = self.change_error_channel(channel_id)
        except ValueError:
            result = None

        if not result:
            return await ctx.send("Error channel not exists")
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def notes(self, ctx: commands.Context):
        notes = getattr(self, 'notes', None)
        embed = discord.Embed(
            title="Notes",
            description=f"\n".join(notes) or "Nothing To See",
        )

        return await ctx.send(embed=embed)

    @commands.command()
    async def add_note(self, ctx: commands.Context, *, text: str):
        if text is None:
            return

        self.notes.append(text)
        await ctx.message.add_reaction("✅")

def setup(bot):
    """Setup Owner Commands"""
    bot.add_cog(OwnerCommands(bot))