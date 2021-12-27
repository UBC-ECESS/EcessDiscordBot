from typing import Dict, Optional
from utils.Converters import Course
from bs4 import BeautifulSoup
import re
import aiohttp


def get_course_url(dept: str, course: str):
    return f"https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept={dept}&course={course}"


async def scrape_course_info(
    course: Course, session: aiohttp.ClientSession = None
) -> Optional[Dict[str, str]]:
    url = get_course_url(course.dept, course.course)
    should_close: bool = False
    if session is None:
        session = aiohttp.ClientSession()
        should_close = True
    try:
        async with session.get(url) as resp:
            soup = BeautifulSoup(await resp.text(), "html.parser")
            name = soup.find(
                lambda predicate: predicate.name == "h4"
                and all(
                    [c.upper() in predicate.text for c in {course.course, course.dept}]
                )
            )
            prereqs = soup.find(
                lambda predicate: predicate.name == "p"
                and "Pre-reqs:" in predicate.text
            )
            coreqs = soup.find(
                lambda predicate: predicate.name == "p" and "Co-reqs:" in predicate.text
            )
            creds = soup.find(
                lambda predicate: predicate.name == "p" and "Credits:" in predicate.text
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
    finally:
        if should_close:
            await session.close()


def get_course_archive_url(dept: str, course: str):
    # Insecure site only since it doesn't look like UBC calendar works over TLS
    return f"http://www.calendar.ubc.ca/vancouver/courses.cfm?page=code&code={dept}"


async def scrape_archive_course_info(
    course: Course, session: aiohttp.ClientSession = None
) -> Optional[Dict[str, str]]:
    url = get_course_archive_url(course.dept, course.course)
    should_close: bool = False
    if session is None:
        session = aiohttp.ClientSession()
        should_close = True
    try:
        async with session.get(url) as resp:
            soup = BeautifulSoup(await resp.text(), "html.parser")
            title = soup.find(
                lambda predicate: predicate.name == "dt"
                and all(
                    [c.upper() in predicate.text for c in {course.course, course.dept}]
                )
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
    except Exception as e:
        print(e)
        return None
    finally:
        if should_close:
            await session.close()
