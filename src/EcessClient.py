"""
Client for the ECESS server
Please ensure `secrets/token.txt` contains the bot's token.
"""
import discord
import os
import traceback
import logging
from discord.ext import commands

from utils.FancyHelp import FancyHelp


def main():
    logging.basicConfig(
        format="(%(levelname)s) [%(asctime)s] %(message)s",
        level=logging.INFO,
        filename="bot_info.log",
        filemode="a",
    )

    # Enable privileged intents
    # Certain methods (eg. `guild.get_members`) require privileged intents
    intents = discord.Intents.default()
    intents.members = True

    # Initialize the client
    client = commands.Bot(intents=intents, command_prefix="!")
    client.bot_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @client.event
    async def on_ready():
        """
        Print a message indicating it is ready
        Primarily for debugging purposes
        """
        logging.info("Bot is ready!")

    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send("This command is on cooldown.")
        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send("You don't have permissions to use this command.")
        elif isinstance(error, commands.errors.MaxConcurrencyReached):
            await ctx.send(
                "This command has reached the max number of concurrent jobs."
            )
        elif isinstance(error, commands.errors.MissingRequiredArgument) or isinstance(
            error, commands.errors.BadArgument
        ):
            # A fresh instance of HelpCommand is required since
            # we must manually pass the context here
            help = FancyHelp()
            help.context = ctx
            await ctx.send("Malformed arguments. Command help:")
            await help.send_group_help(ctx.command)
        else:
            logging.warning(
                "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
            )
            await ctx.send(f"An error occured with the {ctx.command.name} command.")

    @client.command()
    @commands.is_owner()
    async def load(ctx, extension):
        """
        Load the cog extension
        :param extension: extension to be loaded
        """
        client.load_extension(f"cogs.{extension}")

    @client.command()
    @commands.is_owner()
    async def unload(ctx, extension):
        """
        Unload the cog extension
        :param extension: extension to be unloaded
        """
        client.unload_extension(f"cogs.{extension}")

    @client.before_invoke
    async def before_command_invoke(ctx: commands.Context):
        """
        Command logging.
        """
        logging.info(
            f"Command invoked: {ctx.command} by {ctx.author} with message {ctx.message.content}"
        )

    # Parent directory of the bot repo; constructed as parentDir(fileDir(file))
    bot_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load extensions inside of `cogs` directory
    for filename in os.listdir(os.path.join(bot_dir, "src/cogs")):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

    # Read the bot token within `secrets`
    token_file = open(os.path.join(bot_dir, "src/secrets/token.txt"))
    token = token_file.read()

    # Inject a custom help
    client.help_command = FancyHelp()

    # Run the client
    client.run(token)


if __name__ == "__main__":
    main()
