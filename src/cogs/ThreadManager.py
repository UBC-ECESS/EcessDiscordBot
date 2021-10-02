from typing import Dict, Union, List
import discord
from discord.ext import commands, tasks
from utils.JsonTools import read_json, write_json
from utils.Checks import ban_members_check
from utils.Paginator import Paginator

"""
The JSON schema of this file should be:
{
    "<guild_id: str>": [
        <thread_id: int>,
        <thread_id: int>,
        ...
    ],
    ...
}
"""
THREAD_MANAGER_FILENAME: str = "thread_manager.json"

AUTO_ARCHIVE_DURATION: int = 1440


class ThreadManager(commands.Cog):
    """
    Cog for general thread management. Currently, only supports pinning threads.
    (unarchiving them when they get archived)
    This cog is multi-tenant, meaning it can support multiple guilds.
    """

    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.thread_mappings: Dict[str, List[int]] = read_json(THREAD_MANAGER_FILENAME)
        self.thread_refresher_task.start()

    @commands.group(aliases=["t"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def threads(self, ctx: commands.Context):
        """
        Command group related to managing threads.
        """
        if ctx.invoked_subcommand is None:
            raise commands.errors.BadArgument

    @threads.command(aliases=["p"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def pin(self, ctx: commands.Context, thread: discord.Thread):
        """
        Pins a thread; in other words, unarchive it when it gets auto-archived.

        **Example(s)**
          `[p]thread pin #some-thread` - pin the thread #some-thread to unarchive automatically.
        """
        guild_id_str: str = str(ctx.guild.id)
        if thread.id in self.thread_mappings.get(guild_id_str, []):
            return await ctx.reply(f"{thread.mention} is already pinned.")
        else:
            if guild_id_str not in self.thread_mappings:
                self.thread_mappings[guild_id_str] = []
            self.thread_mappings[guild_id_str].append(thread.id)
            write_json(THREAD_MANAGER_FILENAME, self.thread_mappings)
            return await ctx.reply(f"Done! Pinned {thread.mention}")

    @threads.command(aliases=["u"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def unpin(self, ctx: commands.Context, thread: discord.Thread):
        """
        Unpins a thread; in other words, allow it to get archived.

        **Example(s)**
          `[p]thread unpin #some-thread` - unpins the thread #some-thread.
        """
        guild_id_str: str = str(ctx.guild.id)
        if thread.id in self.thread_mappings[guild_id_str]:
            self.thread_mappings[guild_id_str].remove(thread.id)
            write_json(THREAD_MANAGER_FILENAME, self.thread_mappings)
            return await ctx.reply(
                f"Done! Removed {thread.mention} from pinned threads."
            )
        else:
            return await ctx.reply(f"{thread.mention} isn't currently pinned.")

    @threads.command(name="list", aliases=["l"])
    @commands.guild_only()
    @commands.check(ban_members_check)
    async def list_threads(self, ctx: commands.Context):
        """
        List all currently pinned threads.
        """
        guild_id_str: str = str(ctx.guild.id)
        thread_listing: List[str] = []
        for thread_id in self.thread_mappings.get(guild_id_str, []):
            thread: discord.Thread = self.client.get_channel(thread_id)
            if not thread:
                thread_listing.append(f" - `{thread_id}` (error getting thread)")
            else:
                thread_listing.append(f" - {thread.mention} (`{thread_id}`)")
        if not thread_listing:
            return await ctx.reply("No pinned threads.")
        await Paginator(
            title=f"Pinned threads for guild {guild_id_str}",
            entries=thread_listing,
            entries_per_page=25,
        ).paginate(ctx)

    @tasks.loop(seconds=1)
    async def thread_refresher_task(self):
        """
        Threads automatically archive after inactivity. We'll iterate over all the threads
        and unarchive the ones that are archived. This shouldn't be expensive since it doesn't
        make any API calls unless the thread is archived (which was pushed to us by the gateway).

        This task is also equivalent to the one from {CourseThreads.py} but whatever.
        """
        try:
            if self.client.is_ready():
                thread_ids: List[int] = [
                    thread_id
                    for threads in self.thread_mappings.values()
                    for thread_id in threads
                ]

                for thread_id in thread_ids:
                    thread: Union[discord.Thread, None] = self.client.get_channel(
                        thread_id
                    )
                    # If the thread was archived and purged from the bot's cache, the
                    # getter will return None and we'll have to make an API call
                    if thread is None:
                        try:
                            thread: discord.Thread = await self.client.fetch_channel(
                                thread_id
                            )
                        except discord.errors.NotFound:
                            # Thrown if the thread isn't found, which should only happen
                            # if the thread was manually deleted; clean this thread up

                            # NOTE: this should _rarely_ be called. It's a user error if
                            # we ever get to this catch, but we do this defensively.
                            # Also, since it shouldn't get called at all, it's extremely inefficient
                            guild_id_str: Union[None, str] = None
                            for guild, threads in self.thread_mappings.items():
                                if thread_id in threads:
                                    guild_id_str = guild
                                    break
                            if guild_id_str:
                                self.thread_mappings[guild_id_str].remove(thread_id)
                            write_json(THREAD_MANAGER_FILENAME, self.thread_mappings)
                            continue

                    if thread.archived:
                        print(
                            f"Unarchived thread with thread ID: {thread_id}, name: {thread.name}"
                        )
                        await thread.edit(
                            archived=False,
                            auto_archive_duration=AUTO_ARCHIVE_DURATION,
                        )
        except Exception as e:
            print("Thread manager refresher error:", e)


def setup(client: commands.Bot):
    client.add_cog(ThreadManager(client))
