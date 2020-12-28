# Use message reactions to add and remove roles
import discord
from discord.ext import commands

# Constants
ROLE_MSG_ID = 793029981570596875
# TODO use a dictionary to map emotes to roles

# Initalize Client
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(intents=intents, command_prefix = '.')

@client.event
async def on_ready():
    print("Bot is ready!")

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, name="Unassigned Year")
    await client.add_roles(member, role)

@client.event
async def on_raw_reaction_add(payload):
    # TODO refactor to use the guild object
    print("Reaction Added!")
    message_id = payload.message_id
    if message_id == ROLE_MSG_ID:
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

@client.event
async def on_raw_reaction_remove(payload):
    print("Reaction Removed!")
    message_id = payload.message_id
    if message_id == ROLE_MSG_ID:
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
token_file = open("secret_token.txt")
token = token_file.read()
client.run(token)
