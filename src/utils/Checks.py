import discord
from discord.ext import commands


def ban_members_check(ctx: commands.Context):
    return (
        ctx.bot.is_owner(ctx.author)
        or isinstance(ctx.author, discord.Member)
        and ctx.author.guild_permissions.ban_members
    )
