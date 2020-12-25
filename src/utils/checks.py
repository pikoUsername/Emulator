from discord.ext import commands
from discord.ext.commands import check

from src.models import User

def is_owner():
    """A :func:`.check` that checks if the person invoking this command is the
    owner of the bot.

    This is powered by :meth:`.Bot.is_owner`.

    This check raises a special exception, :exc:`.NotOwner` that is derived
    from :exc:`.CheckFailure`.
    """

    async def predicate(ctx):
        user = await User.query.where(User.user_id == ctx.author.id).gino.first()

        if not await ctx.bot.is_owner(ctx.author) or not user.is_owner:
            raise commands.NotOwner('You do not owner.')
        return True

    return check(predicate)