"""
Commands to bring up FAQ resources
"""
import discord
from discord.ext import commands

# Messages linking FAQs documents
programs_msg = (
    "CPEN: https://www.ece.ubc.ca/academic-programs/undergraduate/programs/computer-engineering-program \n"
    "ELEC: https://www.ece.ubc.ca/academic-programs/undergraduate/programs/electrical-engineering-program \n"
    "MASc/MEng: http://www.ece.ubc.ca/admissions/graduate/apply"
)
leetcode_msg = (
    "LC Intro Guide: https://docs.google.com/document/d/16BeYJzj_az-8Zv562RgZ0M_mxvCo6W6Thhc0D1oaNwE/edit?usp=sharing \n"
    "To bring up the Blind75 list, please use `!blind75`"
)
blind75_msg = "Blind75 LC List: https://docs.google.com/spreadsheets/d/1O6lu-27mkdEfQAFfMB43vcqZRF57ygtJO2tCDw2ZQaY/edit?usp=sharing"
repo_msg = (
    "ECESS Discord Bot's Github Repo: https://github.com/kelvinkoon/ecess-discord-bot"
)


class FaqManager(commands.Cog):
    """
    Cog for the FAQ commands
    """

    def __init__(self, client):
        self.client = client

    """
    Bring up ECE program details
    """

    @commands.command()
    async def programs(self, ctx):
        await ctx.send(programs_msg)

    """
    Bring up the LeetCode Intro Prep Guide
    """

    @commands.command()
    async def leetcode(self, ctx):
        await ctx.send(leetcode_msg)

    """
    Bring up the Blind75 LeetCode list
    """

    @commands.command()
    async def blind75(self, ctx):
        await ctx.send(blind75_msg)

    """
    Bring up the bot's Github repository
    """

    @commands.command()
    async def repo(self, ctx):
        await ctx.send(repo_msg)


def setup(client):
    client.add_cog(FaqManager(client))
