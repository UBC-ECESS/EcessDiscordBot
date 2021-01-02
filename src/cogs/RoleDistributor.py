"""
Use reactions to add and remove roles.
Please ensure `secrets/role_msg_id.txt` contains the selected message ID 
"""
import discord
import os.path
from discord.ext import commands


class RoleDistributor(commands.Cog):
    """
    Cog for distributing roles (eg. 2nd Year)
    """

    def __init__(self, client):
        self.client = client

        # Mapping for emoji to role
        self.emote_to_role = {"🚗": "2nd Year", "🚙": "3rd Year", "🏎️": "4th Year"}

        # Parent directory of the bot repo; constructed as parentDir(srcDir(fileDir(file)))
        bot_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        # Role message ID to be receiving reacts
        role_msg_id_file = open(os.path.join(bot_dir, "src/secrets/role_msg_id.txt"))
        self.role_msg_id = int(role_msg_id_file.read())

    """
    Print a message indicating it is ready
    Primarily for debugging purposes
    """

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready!")

    """
    Assign appropriate roles upon adding reactions
    :param payload: object to access member and guild
    """

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        # Verify if selected message is the role message
        if message_id == self.role_msg_id:
            guild = self.client.get_guild(payload.guild_id)

            # Map role to corresponding reaction
            if payload.emoji.name in self.emote_to_role:
                name = self.emote_to_role[payload.emoji.name]
                role = discord.utils.get(guild.roles, name=name)
            else:
                print("Please select either a red_car, blue_car, or race_car.")
                return

            # Assign role to member
            member = payload.member
            if member is not None:
                await member.add_roles(role)
                print("Role assigned!")
            else:
                print("Member not found.")

    """
    Unassign roles upon removing reactions 
    :param payload: object to access member and guild
    """

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        # Verify if selected message is the role message
        if message_id == self.role_msg_id:
            guild = self.client.get_guild(payload.guild_id)
            # Map role to corresponding reaction
            if payload.emoji.name in self.emote_to_role:
                name = self.emote_to_role[payload.emoji.name]
                role = discord.utils.get(guild.roles, name=name)
            else:
                print("Please select either a red_car, blue_car, or race_car.")
                return

            # Unassign role from member
            member = guild.get_member(payload.user_id)
            if member is not None:
                await member.remove_roles(role)
                print("Role removed!")
            else:
                print("Member not found.")


def setup(client):
    client.add_cog(RoleDistributor(client))
