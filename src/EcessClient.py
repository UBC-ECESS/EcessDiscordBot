"""
Client for the ECESS server
Please ensure `secrets/token.txt` contains the bot's token.
"""
import discord
import os
import traceback
from discord.ext import commands


def main():
    # Enable privileged intents
    # Certain methods (eg. `guild.get_members`) require privileged intents
    intents = discord.Intents.default()
    intents.members = True

    # Initialize the client
    client = commands.Bot(intents=intents, command_prefix="!")

    @client.event
    async def on_ready():
        """
        Print a message indicating it is ready
        Primarily for debugging purposes
        """
        print("Bot is ready!")

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
            help = commands.help.DefaultHelpCommand()
            help.context = ctx
            await ctx.send("Malformed arguments. Command help:")
            await help.send_command_help(ctx.command)
        else:
            print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
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

    # Parent directory of the bot repo; constructed as parentDir(fileDir(file))
    bot_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load extensions inside of `cogs` directory
    for filename in os.listdir(os.path.join(bot_dir, "src/cogs")):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

    # Read the bot token within `secrets`
    token_file = open(os.path.join(bot_dir, "src/secrets/token.txt"))
    token = token_file.read()

    # Run the client
    client.run(token)


if __name__ == "__main__":
    main()
