import logging
from typing import Callable, Dict, Optional
from aiohttp.client_exceptions import ClientOSError

from utils.Converters import Course
from bs4 import BeautifulSoup
import re
import aiohttp
import asyncio

RETRY_COUNT: int = 3


def get_course_url(dept: str, course: str):
    return f"https://vancouver.calendar.ubc.ca/course-descriptions/subject/{dept.lower()}v"


async def _request_retry_wrapper(
    url: str, parser: Callable[[str], Dict[str, str]]
) -> Optional[Dict[str, str]]:
    for try_count in range(RETRY_COUNT):
        try:
            async with aiohttp.request("GET", url) as resp:
                return parser(await resp.text())
        except ClientOSError as e:
            logging.error(f"Error: {e}, try count: {try_count}")
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(f"Fatal error, aborting: {e}")
            return None


async def scrape_course_info(course: Course) -> Optional[Dict[str, str]]:
    url: str = get_course_url(course.dept, course.course)

    def parser(content: str):
        soup = BeautifulSoup(content, "html.parser")
        course_container = soup.find(
            lambda predicate: predicate.name == "div" and "text-formatted" in predicate.get("class", [])
            and all([c.upper() in predicate.text for c in {course.course, course.dept}])
        )

        title = course_container.find(
            lambda predicate: predicate.name == "h3"
        )

        if not title:
            return None

        description = course_container.find(
            lambda predicate: predicate.name == "p"
        )

        credits, name, prereqs, coreqs, desc = (
            None,
            None,
            "None",
            "None",
            description.text,
        )
        title_parse = re.search(r"(?:[\S\s]+?)\(([0-9]+?)\)([\S\s]+)", title.text)
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
            "name": f"{course.dept} {course.course} {name.strip()}",
            "description": desc.strip(),
            "prerequisites": prereqs.strip(),
            "corequisites": coreqs.strip(),
            "credits": str(credits),
            "footer": "Source: UBC Course Schedule (Vancouver)",
        }

    return await _request_retry_wrapper(url, parser)
