"""
Commands to verify prerequisites for ECE/CS courses
"""
import discord
from discord.ext import commands
from utils.Converters import Course

from utils.UBCCourseInfo import scrape_course_info


class PrerequisiteChecker(commands.Cog):
    """
    Cog for the prerequisite check commands
    """

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def courseinfo(self, ctx, course: Course):
        """
        Get a simplified view of the course info.
        Make sure the course is in the form of DEPT### (case-insensitive).
        """
        course_info = await scrape_course_info(course)
        if course_info is None:
            return await ctx.send("Course not found.")
        em = discord.Embed(title=course_info["name"], url=course_info["url"])
        em.set_footer(text=course_info["footer"])
        em.add_field(
            name="Prerequisites", inline=False, value=course_info["prerequisites"]
        )
        em.add_field(
            name="Corequisites", inline=False, value=course_info["corequisites"]
        )
        em.add_field(name="Credits", value=course_info["credits"])
        em.add_field(name="Description", inline=False, value=course_info["description"])
        await ctx.send(embed=em)


def setup(client):
    client.add_cog(PrerequisiteChecker(client))
