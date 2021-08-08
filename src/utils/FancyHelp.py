from typing import List
from discord.ext import commands
from utils.Paginator import Paginator


class FancyHelp(commands.MinimalHelpCommand):
    """
    A help formatter that leverages commands.MinimalHelpCommand, with some
    additional formatting using a custom paginator.
    """

    async def send_pages(self):
        help_lines: List[str] = []
        for page in self.paginator.pages:
            for line in page.splitlines():
                help_lines.append(line)
        return await Paginator(
            title=self.commands_heading, entries=help_lines, entries_per_page=25
        ).paginate(self.context)

    def get_command_signature(self, command: commands.Command):
        return f"`{super().get_command_signature(command)}`"

    def add_subcommand_formatting(self, command: commands.Command):
        fmt = "`{0}{1}` \N{EN DASH} {2}" if command.short_doc else "`{0}{1}`"
        self.paginator.add_line(
            fmt.format(
                self.context.clean_prefix, command.qualified_name, command.short_doc
            )
        )

    def add_command_formatting(self, command: commands.Command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def add_aliases_formatting(self, aliases: List[str]):
        self.paginator.add_line(
            f'**{self.aliases_heading}** {", ".join([f"`{alias}`" for alias in aliases])}',
            empty=True,
        )

    def add_bot_commands_formatting(self, commands: commands.Command, heading: str):
        if commands:
            joined: str = "\n".join(f"`{c.name}` - {c.short_doc}" for c in commands)
            self.paginator.add_line(f"\n__**{heading}**__")
            self.paginator.add_line(joined)
