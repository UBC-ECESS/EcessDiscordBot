from typing import List
from discord.ext import commands
from utils.Paginator import Paginator


class FancyHelp(commands.MinimalHelpCommand):
    """
    A help formatter that leverages commands.MinimalHelpCommand, with some
    additional formatting using a custom paginator.
    """

    def __init__(self, **options):
        super().__init__(**options)
        self.no_category = "Uncategorized"

    async def send_pages(self):
        help_lines: List[str] = []
        for page in self.paginator.pages:
            for line in page.splitlines():
                help_lines.append(line)
        return await Paginator(
            title=self.commands_heading, entries=help_lines, entries_per_page=25
        ).paginate(self.context)

    def get_command_signature(self, command: commands.Command):
        """Overridden to wrap the command in a code block."""
        return f"`{super().get_command_signature(command)}`"

    def add_subcommand_formatting(self, command: commands.Command):
        """Overridden to wrap the command in a code block."""
        fmt = "`{0}{1}` \N{EN DASH} {2}" if command.short_doc else "`{0}{1}`"
        self.paginator.add_line(
            fmt.format(
                self.context.clean_prefix, command.qualified_name, command.short_doc
            )
        )

    def add_aliases_formatting(self, aliases: List[str]):
        """Overridden to wrap aliases in a code block."""
        self.paginator.add_line(
            f'**{self.aliases_heading}** {", ".join([f"`{alias}`" for alias in aliases])}',
            empty=True,
        )

    def add_bot_commands_formatting(self, commands: commands.Command, heading: str):
        """Overridden to add the short description to the commands list."""
        if commands:
            joined: str = "\n".join(f"`{c.name}` - {c.short_doc}" for c in commands)
            self.paginator.add_line(f"\n__**{heading}**__")
            self.paginator.add_line(joined)

    async def send_group_help(self, group):
        """Overridden in order to handle both group and regular commands."""
        self.add_command_formatting(group)

        filtered = await self.filter_commands(
            getattr(group, "commands", []), sort=self.sort_commands
        )
        if filtered:
            note = self.get_opening_note()
            if note:
                self.paginator.add_line(note, empty=True)

            self.paginator.add_line(f"**{self.commands_heading}**")
            for command in filtered:
                self.add_subcommand_formatting(command)

            note = self.get_ending_note()
            if note:
                self.paginator.add_line()
                self.paginator.add_line(note)

        await self.send_pages()
