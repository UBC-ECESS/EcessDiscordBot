"""
Commands to verify prerequisites for ECE/CS courses
"""
import discord
from discord.ext import commands
import csv
import os

"""
Cog for the prerequisite check commands
:param cog: Inheriting the Cog class
"""
class PrerequisiteChecker(commands.Cog):
    def __init__(self, client): 
        self.client = client

    @commands.command()
    async def prereq(self, ctx, arg):

        # A lot of error checking and log messages
        if len(arg) != 7:
            await ctx.send("Invalid Input")
            return

        program = arg[0:4]
        if program != "cpen" and program != "elec":
            await ctx.send("Unable to identify specified program")
            return

        courseNumString = arg[4:7]
        try:
            int(courseNumString)
        except: 
            await ctx.send("Invalid Course Number")
            return          

        # Parent directory of the bot repo; constructed as parentDir(srcDir(fileDir(file)))
        botDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        course_info_file = open(os.path.join(botDir, 'assets/ece-course-prereqs.csv'), mode='r')

        # Store course info csv as a collection of dictionaries
        csv_reader = csv.DictReader(course_info_file, delimiter=',')
        
        for row in csv_reader:
            # Send course information if matching course number found
            if row['Course'].lower() == arg:
                await ctx.send(f"Course Name: {row['Name']}\nPrerequisites: {row['Prerequisites']}\nCorequisites: {row['Corequisites']}\nCourse Page: {row['URL']}")
                return

        await ctx.send("Course Not Found")
        return

def setup(client):
    client.add_cog(PrerequisiteChecker(client))
