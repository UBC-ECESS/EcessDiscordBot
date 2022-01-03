from typing import Optional
import discord


class ConfirmationView(discord.ui.View):
    def __init__(self, invoking_user: discord.User, timeout: int = 20):
        super().__init__(timeout=timeout)
        self.invoking_user: discord.User = invoking_user
        self.interacted: bool = False
        self.intr_continue: bool = True
        self.followup_webhook: Optional[discord.Webhook] = None

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.green)
    async def _intr_continue(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.interacted = True
        self.intr_continue = True
        self.followup_webhook = interaction.followup
        self.stop()
        await interaction.response.defer()  # ACK the interaction

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def _intr_cancel(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.interacted = True
        self.intr_continue = False
        self.followup_webhook = interaction.followup
        self.stop()
        await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.invoking_user.id