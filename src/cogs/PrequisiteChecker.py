"""
Commands to verify prerequisites for ECE/CS courses
"""
import discord
from discord.ext import commands
import csv
import os


class PrerequisiteChecker(commands.Cog):
    """
    Cog for the prerequisite check commands
    """

    def __init__(self, client):
        self.client = client

        # Parent directory of the bot repo; constructed as parentDir(srcDir(fileDir(file)))
        bot_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        course_info_file = open(
            os.path.join(bot_dir, "assets/ece-course-prereqs.csv"), mode="r"
        )

        # Store course info csv as a dictionary with course name
        course_info_dict = {}
        csv_reader = csv.DictReader(course_info_file, delimiter=",")

        for row in csv_reader:
            course_info_dict[row["Course"]] = row

        self.course_info_dict = course_info_dict

    """
    List the provided course's prerequisites and corequisites
    :param arg: the course given as the argument
    """
    @commands.command()
    async def prereq(self, ctx, arg):

        # A lot of error checking and log messages
        # TODO make this error comment more detailed
        if not (7 <= len(arg) <= 8):
            await ctx.send("Invalid Input Length")
            return

        # Verify the program is either CPEN or ELEC
        program = arg[0:4]
        if program.lower() != "cpen" and program.lower() != "elec":
            await ctx.send("Unable to identify specified program")
            return

        # Verify course level is valid
        course_num_string = arg[4:7]
        try:
            int(course_num_string)
        except:
            await ctx.send("Invalid Course Number")
            return

        if arg.upper() in self.course_info_dict:
            info = self.course_info_dict[arg.upper()]
            await ctx.send(
                f"Course Name: {info['Name']}\nPrerequisites: {info['Prerequisites']}\nCorequisites: {info['Corequisites']}\nCourse Page: {info['URL']}"
            )
        else:
            await ctx.send("Course Not Found. Make sure input has no spaces.")
    
def setup(client):
    client.add_cog(PrerequisiteChecker(client))
