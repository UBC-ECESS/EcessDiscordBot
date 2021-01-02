"""
Commands to verify prerequisites for ECE/CS courses
"""
import discord
from discord.ext import commands

"""
Cog for the prerequisite check commands
:param cog: Inheriting the Cog class
"""


class PrerequisiteChecker(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")


def setup(client):
    client.add_cog(PrerequisiteChecker(client))
