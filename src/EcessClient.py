"""
Client for the ECESS server
Responsible for loading the cog extensions
"""
import discord
import os
from discord.ext import commands

def main():
    # Enable privileged intents 
    # Certain methods (eg. `guild.get_members`) require privileged intents
    intents = discord.Intents.default()
    intents.members = True

    # Initialize the client
    client = commands.Bot(intents=intents, command_prefix='.')

    """
    Load the cog extension
    :param extension: extension to be loaded
    """
    @client.command()
    async def load(ctx, extension):
        client.load_extension(f'cogs.{extension}')

    """
    Unload the cog extension
    :param extension: extension to be unloaded
    """
    @client.command()
    async def unload(ctx, extension):
        client.unload_extension(f'cogs.{extension}')

    # Load extensions inside of `cogs` directory
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')

    # Read the bot token within `secrets`
    token_file = open("secrets/token.txt")
    token = token_file.read()

    # Run the client
    client.run(token)

if __name__ == "__main__":
    main()
