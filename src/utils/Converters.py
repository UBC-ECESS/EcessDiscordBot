from __future__ import annotations
from typing import Optional
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
    def parse(cls, raw: str) -> Optional[Course]:
        match = re.search(r"\b([A-Za-z]{4})([0-9]{3}[A-Za-z]{0,1})\b", raw)
        if not match:
            return None
        dept, course = match.groups()
        if not dept or not course:
            return None
        return Course(dept=dept, course=course)

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Course:
        if len(argument) > MAX_COURSE_STR_LENGTH:
            raise commands.errors.BadArgument
        parsed_course: Optional[Course] = cls.parse(argument)
        if parsed_course is None:
            raise commands.errors.BadArgument
        return parsed_course
