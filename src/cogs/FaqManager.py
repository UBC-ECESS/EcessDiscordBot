"""
Commands to bring up FAQ resources
"""
import discord
from discord.ext import commands

"""
Cog for the FAQ commands
:param cog: Inheriting the Cog class
"""
class FaqManager(commands.Cog):
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

    """
    Bring up the LeetCode Intro Prep Guide
    :param ctx: context command invoked under
    """
    @commands.command()
    async def leetcode(self, ctx):
        msg = ("LC Intro Guide: https://docs.google.com/document/d/16BeYJzj_az-8Zv562RgZ0M_mxvCo6W6Thhc0D1oaNwE/edit?usp=sharing")
        await ctx.send(msg)

    """
    Bring up the Blind75 LeetCode list
    :param ctx: context command invoked under
    """
    @commands.command()
    async def blind75(self, ctx):
        msg = ("Blind75 LC List: https://docs.google.com/spreadsheets/d/1O6lu-27mkdEfQAFfMB43vcqZRF57ygtJO2tCDw2ZQaY/edit?usp=sharing")
        await ctx.send(msg)

def setup(client):
    client.add_cog(FaqManager(client))
