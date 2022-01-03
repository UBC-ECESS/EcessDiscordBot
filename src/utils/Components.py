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

    def add_item(self, item: discord.ui.Item) -> None:
        """
        Add an item to the view, making sure that the confirmation buttons are always last.
        """
        cancel_button: discord.ui.Item = self.children[-1]
        continue_button: discord.ui.Item = self.children[-2]
        self.remove_item(cancel_button)
        self.remove_item(continue_button)
        super().add_item(item)
        super().add_item(continue_button)
        super().add_item(cancel_button)

    def stop(self) -> None:
        """
        Stops this confirmation view and removes its listeners. Note that the original message
        with this view should be edited or modified to resend this in order to reflect the disabled
        components in the client's view.
        """
        super().stop()
        for child in self.children:
            # Future items may not have a disabled attribute
            # Use a guard to prevent errors in the future
            if hasattr(child, "disabled"):
                child.disabled = True
