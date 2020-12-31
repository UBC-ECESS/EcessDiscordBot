"""
Commands to bring up FAQ resources
"""
import discord
from discord.ext import commands

"""
Cog for the FAQ commands
:param cog: Inheriting the Cog class
"""
class FaqGuru(commands.Cog):
    def __init__(self, client): 
        self.client = client

    """
    Bring up ECE program details
    :param ctx: context command invoked under
    """
    @commands.command()
    async def programs(self, ctx):
        msg = ("CPEN: https://www.ece.ubc.ca/academic-programs/undergraduate/programs/computer-engineering-program \n"
               "ELEC: https://www.ece.ubc.ca/academic-programs/undergraduate/programs/electrical-engineering-program \n"
               "MASc/MEng: http://www.ece.ubc.ca/admissions/graduate/apply")
        await ctx.send(msg)

def setup(client):
    client.add_cog(FaqGuru(client))
