"""
Commands to verify prerequisites for ECE/CS courses
"""
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import csv
import os
import aiohttp
import re


class CourseConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if len(argument) > 8:
            raise commands.errors.BadArgument
        match = re.search(r"\b([A-Za-z]{4})([0-9]{3}[A-Za-z]{0,1})\b", argument)
        if match:
            dept, course = match.groups()
            if not dept or not course:
                raise commands.errors.BadArgument
            else:
                return {"dept": dept, "course": course}
        else:
            raise commands.errors.BadArgument


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
        self.session = aiohttp.ClientSession()

    @commands.command()
    async def prereq(self, ctx, arg):
        """
        List the provided course's prerequisites and corequisites
        :param arg: the course given as the argument
        """
        # A lot of error checking and log messages
        # TODO make this error comment more detailed
        if not (7 <= len(arg) <= 8):
            await ctx.send("Invalid input length.")
            return

        # Verify the program is either CPEN or ELEC
        program = arg[0:4]
        if (
            program.lower() != "cpen"
            and program.lower() != "elec"
            and program.lower() != "cpsc"
        ):
            await ctx.send("Unable to identify specified program.")
            return

        # Verify course level is valid
        course_num_string = arg[4:7]
        try:
            int(course_num_string)
        except:
            await ctx.send("Invalid course number.")
            return

        if arg.upper() in self.course_info_dict:
            info = self.course_info_dict[arg.upper()]
            em = discord.Embed(title=info["Name"], url=info["URL"])
            em.add_field(
                name="Prerequisites", inline=False, value=info["Prerequisites"]
            )
            em.add_field(name="Corequisites", inline=False, value=info["Corequisites"])
            em.add_field(name="Description", inline=False, value=info["Description"])
            await ctx.send(embed=em)
        else:
            await ctx.send("Course Not Found. Make sure input has no spaces.")

    @commands.command()
    async def courseinfo(self, ctx, course: CourseConverter):
        """
        Get a simplified view of the course info.
        Make sure the course is in the form of DEPT### (case-insensitive).
        """
        course_info = await self._scrape_course_info(course)
        if course_info is None:
            course_info = await self._scrape_archive_course_info(course)
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

    @staticmethod
    def _get_course_url(dept, course):
        return f"https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept={dept}&course={course}"

    async def _scrape_course_info(self, course):
        url = self._get_course_url(course["dept"], course["course"])
        try:
            async with self.session.get(url) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                name = soup.find(
                    lambda predicate: predicate.name == "h4"
                    and all([c.upper() in predicate.text for c in course.values()])
                )
                prereqs = soup.find(
                    lambda predicate: predicate.name == "p"
                    and "Pre-reqs:" in predicate.text
                )
                coreqs = soup.find(
                    lambda predicate: predicate.name == "p"
                    and "Co-reqs:" in predicate.text
                )
                creds = soup.find(
                    lambda predicate: predicate.name == "p"
                    and "Credits:" in predicate.text
                )
                if not name:
                    return None
                return {
                    "url": url,
                    "name": name.text.strip(),
                    "description": name.next_sibling.text.strip(),
                    "prerequisites": prereqs.text.replace("Pre-reqs:", "").strip()
                    if prereqs
                    else "None",
                    "corequisites": coreqs.text.replace("Co-reqs:", "").strip()
                    if coreqs
                    else "None",
                    "credits": creds.text.replace("Credits:", "").strip()
                    if creds
                    else "Not found",
                    "footer": "Source: UBC Course Schedule",
                }
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def _get_course_archive_url(dept, course):
        # Insecure site only since it doesn't look like UBC calendar works over TLS
        return f"http://www.calendar.ubc.ca/vancouver/courses.cfm?page=code&code={dept}"

    async def _scrape_archive_course_info(self, course):
        url = self._get_course_archive_url(course["dept"], course["course"])
        try:
            async with self.session.get(url) as resp:
                soup = BeautifulSoup(await resp.text(), "html.parser")
                title = soup.find(
                    lambda predicate: predicate.name == "dt"
                    and all([c.upper() in predicate.text for c in course.values()])
                )
                if not title:
                    return None
                desc = title.find_next("dd")
                credits, name, prereqs, coreqs, desc = (
                    None,
                    None,
                    "None",
                    "None",
                    desc.text,
                )
                title_parse = re.search(
                    r"(?:[\S\s]+?)\(([0-9]+?)\)([\S\s]+)", title.text
                )
                if not title_parse:
                    return None
                pres = re.search(r"(?:Prerequisite\:)([\S\s]+?\.)", desc)
                cos = re.search(r"(?:Corequisite\:)([\S\s]+?\.)", desc)
                credits, name = title_parse.groups()
                desc = desc.replace(
                    "This course is not eligible for Credit/D/Fail grading.", ""
                )
                if pres:
                    prereqs = pres.group(1)
                    desc = desc.replace(pres.group(0), "")
                if cos:
                    coreqs = cos.group(1)
                    desc = desc.replace(cos.group(0), "")
                return {
                    "url": url,
                    "name": f"{course['dept'].upper()} {course['course']} {name.strip()}",
                    "description": desc.strip(),
                    "prerequisites": prereqs.strip(),
                    "corequisites": coreqs.strip(),
                    "credits": str(credits),
                    "footer": "Source: UBC Course Archive",
                }
        except Exception as e:
            print(e)
            return None


def setup(client):
    client.add_cog(PrerequisiteChecker(client))
