from __future__ import annotations
from discord.ext import commands
import re


MAX_COURSE_STR_LENGTH = 8


class Course:
    def __init__(self, *, dept: str, course: str):
        self._dept: str = dept.upper()
        self._course: str = course.upper()

    @property
    def dept(self) -> str:
        return self._dept

    @property
    def course(self) -> str:
        return self._course

    @property
    def year_level(self) -> str:
        return self._course[0]

    def __str__(self) -> str:
        return f"{self.dept} {self.course}"

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Course:
        if len(argument) > MAX_COURSE_STR_LENGTH:
            raise commands.errors.BadArgument
        match = re.search(r"\b([A-Za-z]{4})([0-9]{3}[A-Za-z]{0,1})\b", argument)
        if match:
            dept, course = match.groups()
            if not dept or not course:
                raise commands.errors.BadArgument
            else:
                return Course(dept=dept, course=course)
        else:
            raise commands.errors.BadArgument
