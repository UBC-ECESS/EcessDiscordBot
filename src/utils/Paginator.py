from typing import Callable, Dict, List
import discord
from discord.ext import commands


class Paginator:
    """A paginator for a list of text."""

    def __init__(
        self,
        *,
        title: str,
        entries: List[str],
        entries_per_page: int = 10,
        wrap_code: bool = False,
    ):
        self.entries: List[str] = entries
        self.title: str = title
        self.entries_per_page: int = entries_per_page
        self.wrap_code: bool = wrap_code

        self.pages: List[discord.Embed] = []
        self.current_page: int = 0

        self.author: discord.Member = None
        self.original_message: discord.Message = None

        self._controls: Dict[str, Callable] = {
            "«": self._go_first,
            "<": self._go_back,
            ">": self._go_next,
            "»": self._go_last,
        }

    async def _go_first(self, _: discord.Interaction):
        if self.current_page != 0:
            self.current_page = 0
            await self.message.edit(embed=self.pages[self.current_page])

    async def _go_back(self, _: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.message.edit(embed=self.pages[self.current_page])

    async def _go_next(self, _: discord.Interaction):
        if self.current_page < (len(self.pages) - 1):
            self.current_page += 1
            await self.message.edit(embed=self.pages[self.current_page])

    async def _go_last(self, _: discord.Interaction):
        if self.current_page != (len(self.pages) - 1):
            self.current_page = len(self.pages) - 1
            await self.message.edit(embed=self.pages[self.current_page])

    async def _check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id

    async def paginate(self, ctx: commands.Context):
        paged_entries: List[List[str]] = [
            self.entries[x : x + self.entries_per_page]
            for x in range(0, len(self.entries), self.entries_per_page)
        ]
        for index, page in enumerate(paged_entries):
            embed = discord.Embed(
                title=f"{self.title} - {index + 1} of {len(paged_entries)}"
            )
            embed.description = "\n".join(page)
            if self.wrap_code:
                embed.description = f"""```
                {embed.description}
                ```"""
            self.pages.append(embed)

        if not self.pages:
            raise ValueError("There must be at least one page to paginate.")

        self.author = ctx.author
        self.message = ctx.message

        view = discord.ui.View()
        view.interaction_check = self._check

        if len(self.pages) > 1:
            for text, callback in self._controls.items():
                button = discord.ui.Button(style=discord.ButtonStyle.secondary)
                button.label = text
                button.callback = callback
                view.add_item(button)

        self.message = await ctx.send(embed=self.pages[0], view=view)
