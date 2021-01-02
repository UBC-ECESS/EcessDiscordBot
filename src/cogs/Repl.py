"""
Commands to execute random code.
"""
import aiohttp
import os
import re
import discord
from discord.ext import commands


MAX_MESSAGE_LENGTH = 2000
MAX_LINE_LENGTH = 15


class Code(commands.Converter):
    """
    Converter to grep markdown code block.
    """

    async def convert(self, ctx, argument):
        match = re.search(r"\`\`\`(?:[\S]*)\n([\s\S]*)\`\`\`", ctx.message.content)
        return match.group(1) if match else None


class Repl(commands.Cog):
    """
    Cog to run an external coderunner.
    """

    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()
        self.repl_file = f"{os.path.dirname(__file__)}/../secrets/repl_endpoint.txt"
        self.repl_endpoint = (
            open(self.repl_file).read() if os.path.exists(self.repl_file) else None
        )

    @commands.command()
    @commands.max_concurrency(2)
    async def repl(self, ctx, language: str, code: Code):
        """Run code. Supports java, python, and javascript (node) as the language parameter.
        Code parameter should be in a code block."""
        if self.repl_endpoint:
            msg = await ctx.send(f"```Running...```")
            async with self.session.post(
                self.repl_endpoint, json={"language": language, "code": code}
            ) as resp:
                output = await resp.text()

                if (
                    len(str(output)) > MAX_MESSAGE_LENGTH
                    or len(output.splitlines()) > MAX_LINE_LENGTH
                ):
                    filename = f"{ctx.message.id}.txt"
                    with open(filename, "w") as f:
                        f.write(output)
                    with open(filename, "rb") as f:
                        await ctx.send(
                            f"{ctx.author.mention} Uploaded output to file since content was too long.",
                            file=discord.File(f, "output.txt"),
                        )
                    os.remove(filename)
                    await msg.delete()
                else:
                    await msg.edit(
                        content=f"{ctx.author.mention}```\n{output or 'No output.'}```",
                        allowed_mentions=discord.AllowedMentions.none()
                    )
        else:
            return await ctx.send(
                "Repl endpoint isn't initialized. Ask the owner to set it with `!set_repl <endpoint>`"
            )

    @commands.command()
    @commands.is_owner()
    async def set_repl(self, ctx, endpoint: str):
        """Sets the repl endpoint. Should be a full URL with protocol."""
        if not endpoint.startswith("http"):
            return await ctx.send(
                "You're probably missing the protocol (http/s). Try again."
            )
        with open(self.repl_file, "w") as f:
            f.write(endpoint)
        self.repl_endpoint = endpoint
        await ctx.send(f"Set the endpoint to `{endpoint}`.")


def setup(client):
    client.add_cog(Repl(client))
