from typing import List
from discord.ext import commands
from utils.Paginator import Paginator

SHORT_DOC_PREFIX_REPLACEMENT = "[p]"


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

    def _replace_prefix_placeholder(self, content: str):
        return (content or "").replace(
            SHORT_DOC_PREFIX_REPLACEMENT, self.context.clean_prefix
        )

    def add_command_formatting(self, command):
        """Overridden to replace the short_doc."""
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)

        if command.help:
            help_str = self._replace_prefix_placeholder(command.help)
            try:
                self.paginator.add_line(help_str, empty=True)
            except RuntimeError:
                for line in help_str.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()

    def add_subcommand_formatting(self, command: commands.Command):
        """Overridden to wrap the command in a code block and also replace the short_doc."""
        fmt = "`{0}{1}` \N{EN DASH} {2}" if command.short_doc else "`{0}{1}`"
        self.paginator.add_line(
            fmt.format(
                self.context.clean_prefix,
                command.qualified_name,
                self._replace_prefix_placeholder(command.short_doc),
            )
        )

    def add_aliases_formatting(self, aliases: List[str]):
        """Overridden to wrap aliases in a code block."""
        self.paginator.add_line(
            f'**{self.aliases_heading}** {", ".join([f"`{alias}`" for alias in aliases])}',
            empty=True,
        )

    def add_bot_commands_formatting(self, commands: commands.Command, heading: str):
        """Overridden to add the short description to the commands list and also to replace the short_doc."""
        if commands:
            joined: str = "\n".join(
                f"`{c.name}` - {self._replace_prefix_placeholder(c.short_doc)}"
                for c in commands
            )
            self.paginator.add_line(f"\n__**{heading}**__")
            self.paginator.add_line(joined)

    async def send_group_help(self, group: commands.Group):
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
