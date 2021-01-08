import asyncio

import typing
from contextlib import suppress

from discord.ext import commands
import discord
from discord.errors import DiscordException


class Spammer:
    def __init__(self, bot=None, guild_id: int = None, user_id: int = None, user_ids: typing.List[int] = None):
        if not isinstance(bot, commands.AutoShardedBot):
            raise TypeError("Attribute 'bot' is not commands.AutoShardedBot isinstance")

        self.user_id = user_id
        self._spamming = False
        self.bot = bot
        self.guild_id = guild_id
        self.user_ids = user_ids

    async def spam_with_period_to_channel(
        self,
        bot: commands.AutoShardedBot = None,
        delay: int = 0,
        channel_id: int = None,
        channel_ids: typing.List[int] = None,
        guild_id: int = None,
        **message_params
    ) -> None:
        """
        Sending Message with delay

        :param bot: if None then get from class isinstance
        :param delay: delay for sleep
        :param channel_id:
        :param channel_ids:
        :param guild_id:
        :param message_params: All 'send(*args, **kwargs) attribute
        :return:
        """
        if self._spamming:
            raise RuntimeError("Current Bot Spamming")
        bot = bot or self.bot

        channels = [self.get_channel(guild_id, channel_id, channel_ids, bot=bot)]

        self._spamming = True

        for channel in channels:
            with suppress(DiscordException):
                if not isinstance(channel, discord.TextChannel):
                    raise TypeError("Spamming To Not 'TextChannel'")
                await channel.send(**message_params)
                await asyncio.sleep(delay)

    def get_user(self,
                 bot: commands.AutoShardedBot = None,
                 user_id: int = None,
                 user_ids: typing.List[int] = None
        )-> typing.Union[typing.List[discord.abc.User], discord.abc.User]:
        bot = bot or self.bot
        try:
            if user_id or user_ids is None:
                self._spamming = True
                user = bot.get_user(user_id)
                return user

            if user_id and user_ids:
                raise TypeError("cant Get Both Argument, as the same")

            result = []
            self._spamming = True
            for user_id_ in user_ids:
                user = bot.get_user(user_id_)
                result.append(user)
        except AttributeError as e:
            self._spamming = False
            raise e
        else:
            self._spamming = False
            return result


    def get_channel(self,
                    guild_id: int = None,
                    channel_id: int = None,
                    channel_ids: typing.List[int] = None,
                    *,
                    bot: commands.AutoShardedBot = None
        ) -> typing.Union[typing.List[discord.abc.GuildChannel], discord.abc.GuildChannel]:
        if self.guild_id and guild_id is None:
            raise AttributeError("Attribute 'guild_id' and function 'guild_id' is None")

        bot = bot or self.bot
        guild_id = guild_id or self.guild_id

        try:
            if channel_id:
                self._spamming = True
                channel = bot.get_guild(guild_id).get_channel(channel_id)
                return channel

            if channel_id and channel_ids:
                raise TypeError("Cant Get Both Elements")

            channels = []
            self._spamming = True
            for channel_id_ in channel_ids:
                channel = bot.get_guild(guild_id).get_channel(channel_id_)
                channels.append(channel)
        except AttributeError as e:
            self._spamming = False
            raise e
        else:
            self._spamming = False
            return channels

    async def say_to_user(
            self,
            *,
            bot: commands.AutoShardedBot = None,
            user_id: int = None,
            user_ids: typing.List[int] = None,
            **message_params,
        ) -> None:
        if self._spamming:
            raise RuntimeError("Current Bot Spamming")

        if user_id and self.user_id is None:
            raise TypeError("User id Is Not Correct")

        user_ids = user_ids or self.user_ids
        user_id = user_id or self.user_id
        bot = bot or self.bot

        try:
            if user_id:
                self._spamming = True
                user = bot.get_user(user_id)
                await user.send(**message_params)

            if user_id and user_ids:
                raise RuntimeError("Cant Get Both Elements")

            self._spamming = True
            for one_id in user_ids:
                user = bot.get_user(one_id)
                await user.send(**message_params)

        except AttributeError as e:
            self._spamming = False
            raise e
        else:
            self._spamming = False

    async def say_to_channel(self,
                             guild_id: int,
                             channel_id: int,
                             text: str,
                             ctx,
                             bot = None) -> bool:
        try:
            channel = bot.get_guild(guild_id).get_channel(channel_id)
        except AttributeError:
            await ctx.send("Channel and Guild Not Found")
            return False
        except (discord.Forbidden, commands.BotMissingPermissions):
            await ctx.send("Not Enough access")
            return False
        await channel.send(text)
        return True
