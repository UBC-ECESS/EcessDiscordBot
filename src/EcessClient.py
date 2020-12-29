# Use message reactions to add and remove roles
import discord
from discord.ext import commands

# Constants
# TODO keep this in a secret file
# TODO use a dictionary to map emotes to roles
# TODO add javadoc

class EcessClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO initialization logic
        role_msg_id_file = open("secret_role_msg_id.txt")
        role_msg_id = int(role_msg_id_file.read())
        self.ROLE_MSG_ID = role_msg_id

    async def on_ready(self):
        print("Bot is ready!")

    async def on_member_join(self, member):
        role = discord.utils.get(member.server.roles, name="Unassigned Year")
        await client.add_roles(member, role)

    async def on_raw_reaction_add(self, payload):
        # TODO refactor to use the guild object
        print("Reaction Added!")
        message_id = payload.message_id
        if message_id == self.ROLE_MSG_ID:
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)

            if payload.emoji.name == "🚗":
                print("2nd Year Role")
                role = discord.utils.get(guild.roles, name="2nd Year")
            elif payload.emoji.name == "🚙":
                print("3rd Year Role")
                role = discord.utils.get(guild.roles, name="3rd Year")
            elif payload.emoji.name == "🏎️":
                print("4th Year Role")
                role = discord.utils.get(guild.roles, name="4th Year")
            else:
                print("Please select either a red_car, blue_car, or race_car.")
                return
            
            member = payload.member 
            if member is not None:
                await member.add_roles(role)
                print("Role assigned!")
            else:
                print("Member not found.")
    
    async def on_raw_reaction_remove(self, payload):
        print("Reaction Removed!")
        message_id = payload.message_id
        if message_id == self.ROLE_MSG_ID:
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)

            if payload.emoji.name == "🚗":
                print("2nd Year Role")
                role = discord.utils.get(guild.roles, name="2nd Year")
            elif payload.emoji.name == "🚙":
                role = discord.utils.get(guild.roles, name="3rd Year")
            elif payload.emoji.name == "🏎️":
                print("3rd Year Role")
                print("4th Year Role")
                role = discord.utils.get(guild.roles, name="4th Year")
            else:
                print("Please select either a red_car, blue_car, or race_car.")
                return

            # TODO unsure why we need to use the guild methods instead of 
            # directly using the payloads object
            
            member = guild.get_member(payload.user_id)
            if member is not None:
                await member.remove_roles(role)
                print("Role removed!")
            else:
                print("Member not found.")

# Run client on server
# Store bot token in `secret_token.txt`
# Initalize Client
intents = discord.Intents.default()
intents.members = True
client = EcessClient(intents=intents, command_prefix = '.')

token_file = open("secret_token.txt")
token = token_file.read()
client.run(token)
