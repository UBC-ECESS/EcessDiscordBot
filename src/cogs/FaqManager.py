"""
Commands to bring up FAQ resources
"""
import os
import json
from discord.ext import commands


class FaqManager(commands.Cog):
    """
    Cog for the FAQ commands
    """

    def __init__(self, client):
        self.client = client
        default_commands_filepath = os.path.join(
            client.bot_dir, "assets/default_commands.json"
        )
        self.extra_commands_filepath = os.path.join(
            client.bot_dir, "assets/extra_commands.json"
        )
        self.custom_commands = {}

        # Load the default commands
        with open(default_commands_filepath, "r") as f:
            commands = json.loads(f.read())
            for command, metadata in commands.items():
                self._faq_command_add(
                    command, metadata["content"], metadata["description"]
                )

        # Load or initialize the custom commands
        if os.path.exists(self.extra_commands_filepath):
            with open(self.extra_commands_filepath, "r") as f:
                self.custom_commands = json.loads(f.read())
                for command, metadata in self.custom_commands.items():
                    self._faq_command_add(
                        command,
                        metadata["content"],
                        metadata.get("description", metadata["content"]),
                    )
        else:
            self._write_json({}, self.extra_commands_filepath)

    def _faq_command_add(self, name, content, description=None):
        if description is None:
            description = content

        # We skip registering the command under this cog since it doesn't
        # play nicely if it doesn't happen at class intiialization (especially
        # for its interaction with the help menus). Thus it's unbounded.
        command = commands.command(name=name)(self._faq_command(content, description))
        return self.client.add_command(command)

    def _faq_command_remove(self, name):
        return self.client.remove_command(name)

    @staticmethod
    def _faq_command(content, description):
        async def command(ctx):
            await ctx.send(content)

        command.__doc__ = f"{description[:40]}{'...' if len(description) > 40 else ''}"
        return command

    @staticmethod
    def _write_json(payload, file):
        with open(file, "w") as f:
            json.dump(payload, f)

    @commands.command()
    @commands.is_owner()
    async def add(self, ctx, name, *, content):
        """Adds a custom command."""
        try:
            self._faq_command_add(name, content)
        except commands.errors.CommandRegistrationError:
            return await ctx.send("Command name already exists. Try again.")

        # Since we pass the command uniqueness check above, we skip checking
        # whether the command exists here and just overwrite it
        self.custom_commands[name] = {
            "description": content,
            "content": content,
        }
        self._write_json(self.custom_commands, self.extra_commands_filepath)
        await ctx.send(f"Command `{name}` added!")

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, name):
        """Removes a custom command."""
        if name not in self.custom_commands:
            return await ctx.send("Command is not a custom command.")
        self._faq_command_remove(name)
        del self.custom_commands[name]
        self._write_json(self.custom_commands, self.extra_commands_filepath)
        await ctx.send(f"Command `{name}` removed!")


def setup(client):
    client.add_cog(FaqManager(client))
