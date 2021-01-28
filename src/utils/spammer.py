import asyncio
import typing

from discord.ext import commands
import discord

from .mixins import ContextInstanceMixin


class Spammer(ContextInstanceMixin):
    __slots__ = ("spamming", "bot")

    def __init__(self, bot: 'Bot'):
        self._spamming = False
        self.bot = bot

    async def spam_with_period_to_channel(
            self,
            delay: int = 0,
            channel_id: int = None,
            channel_ids: typing.List[int] = None,
            guild_id: int = None,
            **message_params
    ) -> bool:
        """
        Sending Message with delay

        :param delay: delay for sleep
        :param channel_id:
        :param channel_ids:
        :param guild_id:
        :param message_params: All 'send(*args, **kwargs) attribute
        :return:
        """
        if self._spamming:
            raise RuntimeError("Current Bot Spamming")

        channels = [self.get_channel(guild_id, channel_id, channel_ids)]
        self._spamming = True

        try:
            for channel in channels:
                await channel.send(**message_params)
                await asyncio.sleep(delay)
        except commands.BotMissingPermissions or discord.NotFound:
            return False
        finally:
            self._spamming = False
            return True

    def get_user(
            self,
            user_id: int = None,
            user_ids: typing.List[int] = None,
            ) -> typing.Union[typing.List[discord.User], discord.User]:
        """
        Get User Depends at arguments
        """
        if user_id or user_ids is None:
            user = self.bot.get_user(user_id)
            return user

        if user_id and user_ids:
            raise TypeError("cant Get Both Argument, as the same")

        result = []
        for user_id_ in user_ids:
            user = self.bot.get_user(user_id_)
            result.append(user)
        return result

    def get_channel(
            self,
            guild_id: int,
            channel_id: int,
            channel_ids: typing.List[int] = None,
        ):
        """
        GetChannel with many checks

        :param guild_id:
        :param channel_id:
        :param channel_ids:
        """
        bot = self.bot

        if channel_id:
            channel = bot.get_guild(guild_id).get_channel(channel_id)
            return channel

        if channel_id and channel_ids:
            raise TypeError("Cant Get Both Elements")

        channels = []
        for channel_id_ in channel_ids:
            channel = bot.get_guild(guild_id).get_channel(channel_id_)
            channels.append(channel)
        return channels

    async def say_to_user(
            self,
            *,
            user_id: int = None,
            user_ids: typing.List[int] = None,
            **message_params,
    ) -> None:
        if self._spamming:
            raise RuntimeError("Current Bot Spamming")
        if user_ids and user_ids is None:
            raise AttributeError("Attribute 'user_id' and 'users_id' is Empty")

        try:
            if user_id:
                self._spamming = True
                user = self.get_user(user_id)
                await user.send(**message_params)
                return

            if user_id and user_ids:
                raise RuntimeError("Cant Get Both Elements")

            self._spamming = True
            users = self.get_user(user_ids=user_ids)
            for user in users:
                await user.send(**message_params)

        except AttributeError as e:
            self._spamming = False
            raise e
        else:
            self._spamming = False

    async def say_to_channel(self,
                             guild_id: int,
                             channel_id: int,
                             *args,
                             **kwargs,
                             ) -> bool:
        try:
            channel = self.get_channel(guild_id, channel_id)
        except AttributeError:
            return False
        except (discord.Forbidden, commands.BotMissingPermissions):
            return False
        except commands.CommandOnCooldown as exc:
            await asyncio.sleep(int(exc.retry_after))
            await self.say_to_channel(guild_id, channel_id)
        else:
            await channel.send(*args, **kwargs)
            return True
