# ECESS Discord Bot
A work in progress Discord bot to be deployed on the Electrical and Computer Engineering Student Society (ECESS) server. 

The motivation to build a custom bot against using pre-built solutions (such as MEE6) stemmed from the lack of flexibility beyond role distribution. 

## Progress
The following features are currently supported:
- Assigning roles from reaction messages

The following features are currently in progress of being implemented:
- Prerequisite checker commands
- ECE FAQ commands

## Architecture
[Cogs](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html) were used to create modules for each feature. The `EcessClient.py` file will load the available extensions in the `cogs` directory.

## Installation
The bot is currently not live. The instructions are meant for testing on your local machine.
1. Clone the repository.
2. Ensure [Python](https://www.python.org/) is installed. Please also install the [discord.py](https://discordpy.readthedocs.io/en/latest/intro.html#installing) library and check `requirements.txt` file for additional library details. If you can, please use a virtual environment when installing libraries.
3. Within the [Discord Developer Portal](https://discord.com/developers/applications), create a new application. Within the Settings panel, navigate to Bot to create a bot.
4. Create a `secrets` directory, which will hold your private files. Within the `src/secrets` folder, create a `token.txt` file. Copy the token from the Build-A-Bot configuration into the `token.txt` file. Remember not to share your token with anyone.
5. Within the `src/secrets` folder, create a `role_msg_id.txt` file. Enable [Developer Mode](https://discordia.me/en/developer-mode) on your server. Find the message you will be using to assign roles. Right-click and copy the message ID. Copy and paste the message ID into the `role_msg_id.txt` file.
6. Invite the bot into your server through the Developer Portal.  
7. Test the bot by navigating to `src` and running `python3 EcessClient.py`. The bot will be online when the console displays `Bot is ready!`.

## Features
### Role Distribution
The roles are currently mapped to the following emotes.
These can be remapped within the `EcessClient.py` file. 
- :red_car: -> 2nd Year
- :blue_car: -> 3rd Year
- :racing_car: -> 4th Year
Roles will be assigned upon adding a reaction. Roles will be unassigned upon removing a reaction. Reactions consisting of emojis not included above will do nothing.

### Commands
#### Prerequisite Checking (Not Implemented)
ECE course prerequisites can be fetched through using the `.prereq` command with the selected course. For example, using `.prereq cpen333` will list the prerequisites for CPEN333 (System Software Engineering) as CPSC259 or CPEN223.

#### FAQ (Not Implemented)
A Frequently Asked Questions (FAQ) document can be brought up with the `.faq` command. The document will be hosted on Google Drive and will be open to suggestions for all ECE members to contribute.

## Troubleshooting
### SSL Certificate Expiration on Windows
The solution can be found on a Github issue comment [here](https://github.com/Rapptz/discord.py/issues/4159#issuecomment-640107584). Downloading and installing the certificate can be done from [here](https://crt.sh/?id=2835394). The download link can be explicitly found [here](https://beans-took-my-kids.reeee.ee/38qB2n.png).
