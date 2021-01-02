from discord import AsyncWebhookAdapter, Webhook
from discord.ext import commands
import discord
from loguru import logger


async def say_to_user(bot: commands.AutoShardedBot, user_id: int, *args, **kwargs):
    user = Webhook(
        f"https://discord.com/channels/@me/{user_id}",
        adapter=bot.session,
    )
    try:
        await user.send(*args, **kwargs)
    except AttributeError:
        logger.error("User Not Available")
        raise AttributeError("User Not Available")
    except (discord.HTTPException, discord.NotFound):
        user = bot.get_user(user_id)
        await user.send(*args, **kwargs)


async def say_to_channel(bot: commands.AutoShardedBot,
                         guild_id: int,
                         channel_id: int,
                         *args,
                         **kwargs):
    webhook = Webhook.from_url(
        f"https://discord.com/channels/{guild_id}/{channel_id}",
        adapter=AsyncWebhookAdapter(
            bot.session)
    )
    try:
        await webhook.send(*args, **kwargs)
    except (discord.HTTPException, discord.NotFound):
        logger.error("Not Found")
        raise discord.HTTPException("Not Found", message=None)
    except discord.Forbidden:
        logger.error("Forbiddin")
        raise discord.Forbidden("No Access", message=None)
