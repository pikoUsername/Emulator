import glob
import re

import aiofiles
from discord.ext import commands
import discord


class Search(commands.Cog):
    __slots__ = "bot"

    def __init__(self, bot):
        self.bot = bot

    async def search_in_all_files(self, fp: str, regex: str):
        results = []
        for f in glob.glob(f"{fp}/*"):
            async with aiofiles.open(f) as file:
                lines = file.readlines()
                results.append(re.search(regex, "".join(lines)))
                # need to remove lines, bc file could be so huge
                del lines
        return results

    async def search_in_file(self, fp: str, file: str, query: str, regex: bool = False):
        fp += f"/{file}" if fp.endswith('/') else file

        with aiofiles.open(fp, 'r') as f:
            return [m if m in [f'{query}\n', query]  # todo search with regex
                    else None for m in f.readlines()]

    @commands.command(aliases=["s"])
    async def search(self, ctx, *, args: str):
        """
        Command Search in files(file)

        ========= ============================ ===================================
        flag      Meaning                      ShortCut(CUM)
        --------- ---------------------------- -----------------------------------
        --regex   search with regex pattern    -r
        --file    in file                      -f
        --all     in your directory            -a
        --text    required argument find       -t
        ========= ============================ ===================================

        * Default arg is searching in all files.
          You need indicate file or regex.
          IF you didnt see this docs, then you are d***

        For Parsing flags using just argparse, i know it s bad choice.
        But it was a best choice, then others.

        If you saw a bug, please report about this bug!
        """
        import argparse
        parser = argparse.ArgumentParser()

        parser.add_argument('--regex', '-r', required=False, type=str)
        parser.add_argument('--file', '-f', required=False, type=str)
        parser.add_argument('--all', '-a', required=False, default=True)
        parser.add_argument('--text', '-t', required=True, type=str)

        result = parser.parse_args(args)
        e = discord.Embed(color=0x2F3136)
        u_p = self.bot.create_path(ctx.author.id, ctx.guild.id)
        results = []
        # checks for regex, and all, i cant image what can be this
        if getattr(result, 'all', None):
            results.append(
                await self.search_in_all_files(u_p, result.regex)
            )

        if getattr(result, 'regex', None) and hasattr(result, 'text'):
            if len(result.regex) > 3:
                return

            if hasattr(result, 'all'):
                results = await self.search_in_all_files(u_p, result.regex)

            elif hasattr(result, 'file'):
                with open(f"{u_p}/{result.file}") as file:
                    lines = file.readlines()
                    results.append(re.search(result.regex, "".join(lines)))
                    del lines

        if len(results) <= 2048:
            # todo post pastebin
            # post_pastebin(results)
            return

        for r in results:
            for i in range(len(results)):
                e.add_field(name="result", value=str(r))
        else:
            return await ctx.send("No Results Found...")
