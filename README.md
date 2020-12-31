# ECESS Discord Bot
A work in progress Discord bot to be deployed on the [Electrical and Computer Engineering Student Society](http://ubcecess.com/) (ECESS) server. 

The motivation to build a custom bot against using pre-built solutions (such as MEE6) stemmed from the lack of flexibility for additional features beyond role distribution.

## Progress
The following features are currently supported:
- Assigning roles from reaction messages
- ECE FAQ commands

The following features are currently in progress of being implemented:
- Prerequisite checker commands

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
These can be remapped within the `RoleDistributor.py` file. 
- :red_car: -> 2nd Year
- :blue_car: -> 3rd Year
- :racing_car: -> 4th Year

Roles will be assigned upon adding a reaction. Roles will be unassigned upon removing a reaction. Reactions consisting of emojis not included above will do nothing.

### Commands
#### Prerequisite Checking (WIP)
Commands can be found within the `PrerequisiteChecker.py` file.
ECE/CS course prerequisites can be fetched through using the `.prereq` command with the selected course. For example, using `.prereq cpen333` will list the prerequisites for CPEN333 (System Software Engineering) as CPSC259 or CPEN223.

#### FAQ
Commands can be found within the `FaqManager.py` file.
A Frequently Asked Questions (FAQ) document can be brought up with the various commands. In addition, it will link to a document which will be hosted on Google Drive and open to suggestions for all ECE members to contribute.
- `.programs`: Brings up program links for ECE, including MASc and MEng.
- `.leetcode`: Brings up a self-written LeetCode introductory prep guide, which can be found [here](https://docs.google.com/document/d/16BeYJzj_az-8Zv562RgZ0M_mxvCo6W6Thhc0D1oaNwE/edit?usp=sharing)

## Troubleshooting
### SSL Certificate Expiration on Windows
The solution can be found on a Github issue comment [here](https://github.com/Rapptz/discord.py/issues/4159#issuecomment-640107584). Downloading and installing the certificate can be done from [here](https://crt.sh/?id=2835394). The download link can be explicitly found [here](https://beans-took-my-kids.reeee.ee/38qB2n.png).

### Member Not Found on Reaction Removal
Please ensure privileged intents are enabled on the server. Otherwise, `guild.get_members` will not return the proper result.

### Unable to Find Message ID
Please verify Developer Mode has been enabled on your server.
