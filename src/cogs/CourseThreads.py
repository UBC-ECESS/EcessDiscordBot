from typing import Dict, Any, Union, List
import discord
from discord.ext import commands, tasks
from utils.Converters import Course
from utils.JsonTools import read_json, write_json
from utils.Checks import ban_members_check
from utils.Paginator import Paginator

"""
The JSON schema of this file should be:
{
    "<year_level: str>": {
        "base_channel": <channel_id: int>,
        "current_courses": {
            "<course_str>": <thread_id: int>,
            ...
        }
    },
    ...
}
"""
THREADS_CONFIG_FILENAME: str = "thread_channel_mapping.json"
CURRENT_COURSES_KEY: str = "current_courses"
BASE_CHANNEL_KEY: str = "base_channel"

AUTO_ARCHIVE_DURATION: int = 1440


class CourseThreads(commands.Cog):
    """
    Cog for course threads. Note that this entire cog is built upon the idea that
    all threads will be immutable and persistent -- that is, we do not expect threads
    to be deleted; hence, the bot metadata is append-only.
    """

    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.course_mappings: Dict[str, Any] = read_json(THREADS_CONFIG_FILENAME)
        self.thread_refresher_task.start()

    @commands.group(aliases=["ct"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def course_threads(self, ctx: commands.Context):
        """
        Command group related to creating course threads.
        """
        if ctx.invoked_subcommand is None:
            raise commands.errors.BadArgument

    @course_threads.command(aliases=["register", "reg"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def register_base_channel(
        self, ctx: commands.Context, year_level: str, channel: discord.TextChannel
    ):
        """
        Registers a base channel for courses. Note that registering a year is immutable;
        that is, once set and courses are created, it cannot be changed.

        **Example(s)**
          `[p]ct register 1 #some-channel` - registers #some-channel as the base thread for all 1xx level courses
        """
        try:
            int(year_level)
        except ValueError:
            return await ctx.reply(
                f"`{year_level}` isn't a valid integer. This should map to the first digit of the course code."
            )
        if year_level in self.course_mappings and len(
            self.course_mappings[year_level][CURRENT_COURSES_KEY]
        ):
            return await ctx.reply(
                "There are already courses mapped to this year level; changing this is destructive, thus is manual. Exiting."
            )
        await channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False,
            use_private_threads=False,
            use_threads=True,
        )
        self.course_mappings[year_level] = {
            BASE_CHANNEL_KEY: channel.id,
            CURRENT_COURSES_KEY: {},
        }
        write_json(THREADS_CONFIG_FILENAME, self.course_mappings)
        return await ctx.reply(
            f"Done! Added {channel.mention} as the base for year level: `{year_level}`."
        )

    @course_threads.command(aliases=["new", "create"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def create_new_thread(self, ctx: commands.Context, course: Course):
        """
        Creates a new thread for the given course. The course format should be in DEPT###.

        **Example(s)**
          `[p]ct create CPEN331` - creates a new thread for CPEN331
        """
        if course.year_level in self.course_mappings:
            if (
                str(course)
                in self.course_mappings[course.year_level][CURRENT_COURSES_KEY]
            ):
                return await ctx.reply(f"Course `{course}` already exists.")
            base_channel_id: int = self.course_mappings[course.year_level][
                BASE_CHANNEL_KEY
            ]
            base_channel: discord.TextChannel = self.client.get_channel(base_channel_id)
            base_message: discord.Message = await base_channel.send(
                f"Thread for `{course}`"
            )
            created_thread: discord.Thread = await base_message.start_thread(
                name=str(course)
            )
            self.course_mappings[course.year_level][CURRENT_COURSES_KEY][
                str(course)
            ] = created_thread.id
            write_json(THREADS_CONFIG_FILENAME, self.course_mappings)
            return await ctx.reply(
                f"Done! Created thread here: {created_thread.mention}"
            )
        else:
            return await ctx.reply(
                f"Base channel for year level (`{course.year_level}`) doesn't exist. Initialize it with `register_base_channel`."
            )

    async def _does_course_exist(self, ctx: commands.Context, course: Course):
        if (
            course.year_level in self.course_mappings
            and str(course)
            in self.course_mappings[course.year_level][CURRENT_COURSES_KEY]
        ):
            return True
        else:
            await ctx.reply(
                f"A thread for `{course}` doesn't exist.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return False

    @course_threads.command(aliases=["delete", "del"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def delete_thread(self, ctx: commands.Context, course: Course):
        """
        Locks the thread for a given course. Try not to use it as it is relatively destructive.

        **Example(s)**
          `[p]ct delete CPEN331` - removes the thread mapping for CPEN331 and locks the thread
        """
        if not await self._does_course_exist(ctx, course):
            return
        course_thread: discord.Thread = self.client.get_channel(
            self.course_mappings[course.year_level][CURRENT_COURSES_KEY][str(course)]
        )
        await course_thread.edit(locked=True, archived=True)
        del self.course_mappings[course.year_level][CURRENT_COURSES_KEY][str(course)]
        write_json(THREADS_CONFIG_FILENAME, self.course_mappings)
        await ctx.send(f"Done! Locked {course_thread.mention} and removed the mapping.")

    @commands.group(aliases=["c"])
    @commands.guild_only()
    async def courses(self, ctx: commands.Context):
        """
        Command group related to joining, leaving, and listing course threads.

        Note that you could also manually join and leave a thread using Discord's UI.
        """
        if ctx.invoked_subcommand is None:
            raise commands.errors.BadArgument

    @courses.command(name="join")
    @commands.guild_only()
    async def join_course(self, ctx: commands.Context, course: Course):
        """
        Join a course thread, if it exists. Note that this is idempotent.

        Note that there isn't a space between the course and the code.

        **Example(s)**
          `[p]course join CPEN331` - joins the thread for CPEN331
        """
        if not await self._does_course_exist(ctx, course):
            return
        course_thread_id: int = self.course_mappings[course.year_level][
            CURRENT_COURSES_KEY
        ][str(course)]
        course_thread: discord.Thread = self.client.get_channel(course_thread_id)
        await course_thread.add_user(ctx.author)
        return await ctx.reply(
            f"Done! Added you to {course_thread.mention}. You may want to change your notification settings for the thread."
        )

    @courses.command(name="leave")
    @commands.guild_only()
    async def leave_course(
        self, ctx: commands.Context, course: Union[Course, None] = None
    ):
        """
        Leave a course thread, if you're in it. Note that this is idempotent.

        Note that there isn't a space between the course and the code.

        **Example(s)**
          `[p]course leave CPEN331` - leaves the thread for CPEN331
        """
        if not await self._does_course_exist(ctx, course):
            return
        course_thread_id: int = self.course_mappings[course.year_level][
            CURRENT_COURSES_KEY
        ][str(course)]
        course_thread: discord.Thread = self.client.get_channel(course_thread_id)
        await course_thread.remove_user(ctx.author)
        return await ctx.reply(
            f"Done! Removed you from {course_thread.mention}, whether you were in it or not."
        )

    @courses.command(name="list", aliases=["l"])
    @commands.guild_only()
    async def list_courses(self, ctx: commands.Context):
        """
        List all the courses that currently have a course thread.

        **Example(s)**
          `[p]course list` - lists all the courses that currently have a thread
        """
        course_listing: List[str] = []
        for year, year_metadata in self.course_mappings.items():
            course_listing.append(f"**Level `{year}xx`**")
            for course, channel_id in year_metadata[CURRENT_COURSES_KEY].items():
                channel: discord.Thread = self.client.get_channel(channel_id)
                if not channel:
                    course_listing.append(
                        f"  - `{course}`: {channel_id} (error getting thread)"
                    )
                else:
                    course_listing.append(f"  - `{course}`: {channel.mention}")
        await Paginator(
            title="Available Courses", entries=course_listing, entries_per_page=25
        ).paginate(ctx)

    @courses.command(name="search", aliases=["s"])
    @commands.guild_only()
    async def search_courses(self, ctx: commands.Context, query: str):
        """
        Searches the thread directory for a case-insensitive match.

        **Example(s)**
          `[p]course search CPEN` - returns all threads that have CPEN (case-insensitive) in its title
          `[p]course search 331` - returns all threads that have 331 in its title
        """
        search_results: List[str] = []
        for year_metadata in self.course_mappings.values():
            for course, channel_id in year_metadata[CURRENT_COURSES_KEY].items():
                if (
                    query.lower() in course.lower()
                    or query.lower() in course.replace(" ", "").lower()
                ):
                    channel: discord.Thread = self.client.get_channel(channel_id)
                    if not channel:
                        search_results.append(
                            f"- `{course}`: {channel_id} (error getting thread)"
                        )
                    else:
                        search_results.append(f"- `{course}`: {channel.mention}")
        if not search_results:
            return await ctx.reply(
                f"No courses found for `{query}`.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
        await Paginator(
            title=f"Courses Matching: `{query}`", entries=search_results
        ).paginate(ctx)

    @tasks.loop(seconds=1)
    async def thread_refresher_task(self):
        """
        Threads automatically archive after inactivity. We'll iterate over all the threads
        and unarchive the ones that are archived. This shouldn't be expensive since it doesn't
        make any API calls unless the thread is archived (which was pushed to us by the gateway).
        """
        try:
            if self.client.is_ready():
                thread_ids: List[int] = [
                    channel_id
                    for year_metadata in self.course_mappings.values()
                    for channel_id in year_metadata[CURRENT_COURSES_KEY].values()
                ]
                for thread_id in thread_ids:
                    thread: Union[discord.Thread, None] = self.client.get_channel(
                        thread_id
                    )
                    # If the thread was archived and purged from the bot's cache, the
                    # getter will return None and we'll have to make an API call
                    if thread is None:
                        thread: discord.Thread = await self.client.fetch_channel(
                            thread_id
                        )
                    if thread.archived:
                        await thread.edit(
                            archived=False, auto_archive_duration=AUTO_ARCHIVE_DURATION
                        )
        except Exception as e:
            print("Thread refresher error:", e)


def setup(client: commands.Bot):
    client.add_cog(CourseThreads(client))
