"""
Use reactions to add and remove roles.
Please ensure `secrets/role_msg_id.txt` contains the selected message ID 
"""
from json.decoder import JSONDecodeError
import logging
import typing
import discord
import json
import os
from discord.ext import commands


class RoleDistributor(commands.Cog):
    """
    Cog for distributing roles (eg. 2nd Year)
    """

    def __init__(self, client):
        self.client = client

        # Parent directory of the bot repo; constructed as parentDir(srcDir(fileDir(file)))
        bot_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        # Role message ID to be receiving reacts
        self.role_mapping_file = os.path.join(bot_dir, "src/secrets/role_mappings.json")

        if not os.path.exists(self.role_mapping_file):
            self._write_json({}, self.role_mapping_file)

        try:
            with open(self.role_mapping_file, "r") as f:
                self.role_mapping = json.loads(f.read())
        except JSONDecodeError:
            # Self-repair the file, but this means the mapping will be lost
            self._write_json({}, self.role_mapping_file)
            self.role_mapping = {}

        self.role_collector = None

    @commands.command()
    @commands.is_owner()
    async def initialize_role_mapping(
        self, ctx, message: discord.Message, *, options: str = ""
    ):
        """
        Initializes an interactive role mapping session. For more information, type !help initialize_role_mapping

        To map roles, initialize a session by typing:
        !initialize_role_mapping <message_id> <options=[unique,]>

        To add emotes and roles, use the following:
        !add_role_mapping <emote> <role>

        When you're done, type:
        !finalize_role_mapping

        Note that you can have as many messages mapped as you'd like.
        """
        if self.role_collector is not None:
            return await ctx.send(
                "You're already in a mapping session. Finalize it with `!finalize_role_mapping`"
            )

        if ctx.guild.id != message.guild.id:
            return await ctx.send("This message isn't in this guild.")

        if str(message.id) in self.role_mapping:
            await ctx.send(
                "The current message already has a mapping. Do you want to overwrite it? (y/n)"
            )
            reply = await ctx.bot.wait_for(
                "message",
                check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                timeout=30,
            )
            if not reply or reply.content.lower() != "y":
                return await ctx.send("Mapping cancelled.")

        self.role_collector = {
            "message": message,
            "mapping": {},
            "unique": "unique" in options,
        }

        await ctx.send(
            "Session initialized. Add roles by using `!add_role_mapping <emote> <role>`, and finish by using `!finalize_role_mapping`"
        )

    @commands.command()
    @commands.is_owner()
    async def add_role_mapping(
        self, ctx, emote: typing.Union[discord.Emoji, str], role: discord.Role
    ):
        """
        Adds an emote to role mapping to the current interactive session.
        """
        if self.role_collector is None:
            return await ctx.send(
                "You're not in a mapping session. Start one with `!initialize_role_mapping`"
            )

        # We're going to be lazy and not check whether the string is a valid emoji
        if isinstance(emote, str):
            await ctx.send(
                f"Note that `{emote}` should be a valid unicode emote. If it isn't, start over."
            )
            emote_str = emote
        else:
            emote_str = str(emote.id)

        # Verify that we didn't already map the role
        if str(role.id) in self.role_collector["mapping"].values():
            return await ctx.send("This role is already mapped to an emote. Try again.")

        # Verify that the role isn't mapped to another message already
        for message, mapping in self.role_mapping.items():
            mapping = mapping["mapping"]
            if message == str(self.role_collector["message"].id):
                continue
            if str(role.id) in mapping.values():
                return await ctx.send(
                    f"This role is already mapped to an emote in another message. Try again. (message_id: `{message}`)"
                )

        self.role_collector["mapping"][emote_str] = str(role.id)
        await ctx.send(
            f"Successfully added `{emote}` for {role.mention}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command()
    @commands.is_owner()
    async def finalize_role_mapping(self, ctx):
        """
        Finalizes the role mapping.
        """
        if self.role_collector is None:
            return await ctx.send(
                "You're not in a mapping session. Start one with `!initialize_role_mapping`"
            )

        if not self.role_collector["mapping"]:
            await ctx.send("No mappings were added. Cancelling.")
        else:
            self.role_mapping[str(self.role_collector["message"].id)] = {
                "mapping": self.role_collector["mapping"],
                "unique": self.role_collector["unique"],
            }
            self._write_json(self.role_mapping, self.role_mapping_file)
            message = self.role_collector["message"]
            await message.clear_reactions()
            for eid in self.role_collector["mapping"].keys():
                try:
                    emoji = discord.utils.get(self.client.emojis, id=int(eid))
                except ValueError:
                    emoji = eid
                await message.add_reaction(emoji)
            await ctx.send("Done!")

        self.role_collector = None

    @commands.command()
    @commands.is_owner()
    async def list_role_mappings(self, ctx):
        """
        Lists the role mapping to your internal console.
        """
        if len(str(self.role_mapping)) > 2000:
            print(self.role_mapping)
            await ctx.send("Output too long. Check your console output for the log.")
        else:
            await ctx.send(f"```{self.role_mapping}```")

    @commands.command()
    @commands.is_owner()
    async def delete_role_mapping(
        self, ctx, message: typing.Union[discord.Message, str]
    ):
        """
        Deletes a role mapping.
        """
        message_id = message if isinstance(message, str) else message.id
        if str(message_id) not in self.role_mapping:
            return await ctx.send("That message doesn't have a registered listener.")

        del self.role_mapping[str(message_id)]
        self._write_json(self.role_mapping, self.role_mapping_file)
        if isinstance(message, discord.Message):
            await message.clear_reactions()
        await ctx.send("Done!")

    @staticmethod
    def _write_json(payload, file):
        with open(file, "w") as f:
            json.dump(payload, f)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Assign appropriate roles upon adding reactions
        :param payload: object to access member and guild
        """
        if payload.user_id == self.client.user.id:
            return
        # Convert all the IDs to strings since our loaded JSON keys will be strings
        message_id_str = str(payload.message_id)
        emoji_id_str = (
            str(payload.emoji)
            if payload.emoji.is_unicode_emoji()
            else str(payload.emoji.id)
        )

        if message_id_str in self.role_mapping:
            mapping = self.role_mapping[message_id_str]["mapping"]
            unique = self.role_mapping[message_id_str]["unique"]
            guild = self.client.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            message = await self.client.get_channel(payload.channel_id).fetch_message(
                payload.message_id
            )

            if emoji_id_str in mapping:
                role = discord.utils.get(guild.roles, id=int(mapping[emoji_id_str]))
                if member is not None and role is not None:
                    if unique:
                        all_roles = [
                            discord.utils.get(guild.roles, id=int(r))
                            for r in mapping.values()
                        ]
                        await member.remove_roles(
                            *[r for r in all_roles if r in member.roles],
                        )
                        for r in message.reactions:
                            if str(r) != str(payload.emoji):
                                await message.remove_reaction(r.emoji, member)
                    await member.add_roles(role)
                    logging.info(f"Role {role} assigned to {member}!")
                else:
                    logging.info("Member not found, or role was invalid.")
            else:
                await message.remove_reaction(payload.emoji, member)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """
        Unassign roles upon removing reactions
        :param payload: object to access member and guild
        """
        if payload.user_id == self.client.user.id:
            return

        message_id_str = str(payload.message_id)
        emoji_id_str = (
            str(payload.emoji)
            if payload.emoji.is_unicode_emoji()
            else str(payload.emoji.id)
        )

        if message_id_str in self.role_mapping:
            mapping = self.role_mapping[message_id_str]["mapping"]
            guild = self.client.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if emoji_id_str in mapping:
                role = discord.utils.get(guild.roles, id=int(mapping[emoji_id_str]))

                if member is not None and role is not None:
                    await member.remove_roles(role)
                    logging.info(f"Role {role} removed from {member}!")
                else:
                    logging.info("Member not found.")


def setup(client):
    client.add_cog(RoleDistributor(client))
