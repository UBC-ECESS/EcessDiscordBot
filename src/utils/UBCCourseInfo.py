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
    return f"https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept={dept}&course={course}"


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
        name = soup.find(
            lambda predicate: predicate.name == "h4"
            and all([c.upper() in predicate.text for c in {course.course, course.dept}])
        )
        prereqs = soup.find(
            lambda predicate: predicate.name == "p" and "Pre-reqs:" in predicate.text
        )
        coreqs = soup.find(
            lambda predicate: predicate.name == "p" and "Co-reqs:" in predicate.text
        )
        creds = soup.find(
            lambda predicate: predicate.name == "p" and "Credits:" in predicate.text
        )

        return (
            {
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
            if name
            else None
        )

    return await _request_retry_wrapper(url, parser)


def get_course_archive_url(dept: str, course: str):
    # Insecure site only since it doesn't look like UBC calendar works over TLS
    return f"http://www.calendar.ubc.ca/vancouver/courses.cfm?page=code&code={dept}"


async def scrape_archive_course_info(course: Course) -> Optional[Dict[str, str]]:
    url: str = get_course_archive_url(course.dept, course.course)

    def parser(content: str):
        soup = BeautifulSoup(content, "html.parser")
        title = soup.find(
            lambda predicate: predicate.name == "dt"
            and all([c.upper() in predicate.text for c in {course.course, course.dept}])
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
            "footer": "Source: UBC Course Archive",
        }

    return await _request_retry_wrapper(url, parser)
