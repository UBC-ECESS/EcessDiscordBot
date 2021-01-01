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
        # Messages linking FAQs documents
        self.programs_msg = ("CPEN: https://www.ece.ubc.ca/academic-programs/undergraduate/programs/computer-engineering-program \n"
               "ELEC: https://www.ece.ubc.ca/academic-programs/undergraduate/programs/electrical-engineering-program \n"
               "MASc/MEng: http://www.ece.ubc.ca/admissions/graduate/apply")
        self.leetcode_msg = ("LC Intro Guide: https://docs.google.com/document/d/16BeYJzj_az-8Zv562RgZ0M_mxvCo6W6Thhc0D1oaNwE/edit?usp=sharing")
        self.blind75_msg = ("Blind75 LC List: https://docs.google.com/spreadsheets/d/1O6lu-27mkdEfQAFfMB43vcqZRF57ygtJO2tCDw2ZQaY/edit?usp=sharing")

    """
    Bring up ECE program details
    :param ctx: context command invoked under
    """
    @commands.command()
    async def programs(self, ctx):
        await ctx.send(self.programs_msg)

    """
    Bring up the LeetCode Intro Prep Guide
    :param ctx: context command invoked under
    """
    @commands.command()
    async def leetcode(self, ctx):
        await ctx.send(self.leetcode_msg + "\nTo bring up the Blind75 list, please use `.blind75`")

    """
    Bring up the Blind75 LeetCode list
    :param ctx: context command invoked under
    """
    @commands.command()
    async def blind75(self, ctx):
        await ctx.send(self.blind75_msg)

def setup(client):
    client.add_cog(FaqManager(client))
