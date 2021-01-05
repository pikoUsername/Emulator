from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands
import discord
from loguru import logger


async def say_to_user(bot, user_id: int, *args, **kwargs):
    user = bot.get_user(user_id)
    try:
        return await user.send(*args, **kwargs)
    except (discord.HTTPException, discord.NotFound, AttributeError) as e:
        pass

async def say_to_channel(bot: commands.AutoShardedBot,
                         guild_id: int,
                         channel_id: int,
                         *args,
                         **kwargs):
    channel = bot.get_guild(guild_id).get_channel(channel_id)
    try:
        await channel.send(*args, **kwargs)
    except (discord.HTTPException, discord.NotFound):
        logger.error("Not Found")
        raise discord.HTTPException("Not Found", message=None)
    except discord.Forbidden:
        logger.error("Forbidden")
        raise discord.Forbidden("No Access", message=None)
