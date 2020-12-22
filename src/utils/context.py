from discord.ext import commands

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        # we need this for our cache key strategy
        return '<Context>'

    async def show_help(self, command=None):
        """Shows the help command for the specified command if given.
        If no command is given, then it'll show help for the current
        command.
        """
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)
