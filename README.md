# ECESS Discord Bot

A Discord bot to be deployed on the [Electrical and Computer Engineering Student Society](http://ubcecess.com/) (ECESS) server.

The motivation to build a custom bot against using pre-built solutions (such as MEE6) stemmed from the lack of flexibility for additional features beyond role distribution.

## Progress

The following features are currently supported:

- Assigning roles from reaction messages
- ECE FAQ commands
- Prerequisite checker commands

## Architecture

[Cogs](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html) were used to create modules for each feature. The `EcessClient.py` file will load the available extensions in the `cogs` directory. The bot is currently hosted on an AWS EC2 instance.

## Installation

The bot is currently not live. The instructions are meant for testing on your local machine.

1. Clone the repository.
2. Ensure [Python](https://www.python.org/) is installed. Please also install the [discord.py](https://discordpy.readthedocs.io/en/latest/intro.html#installing) library and check `requirements.txt` file for additional library details. If possible, use a virtual environment when installing libraries.
3. Within the [Discord Developer Portal](https://discord.com/developers/applications), create a new application. Within the Settings panel, navigate to Bot to create a bot.
4. Create a `secrets` directory, which will hold your private files. Within the `src/secrets` folder, create a `token.txt` file. Copy the token from the Build-A-Bot configuration into the `token.txt` file. Remember not to share your token with anyone.
5. Within the `src/secrets` folder, create a `role_msg_id.txt` file. Enable [Developer Mode](https://discordia.me/en/developer-mode) on your server. Find the message you will be using to assign roles. Right-click and copy the message ID. Copy and paste the message ID into the `role_msg_id.txt` file.
6. Invite the bot into your server through the Developer Portal. This is found in the OAuth2 section of the Settings. Remember to put the bot on a higher privilege than the roles you are assigning.
7. Test the bot by navigating to `src` and running `python3 EcessClient.py`. The bot will be online when the console displays `Bot is ready!`.
8. (Optional) To format your Python files, run `chmod +x fix_formatting.sh` to enable execute permissions. Proceed to run `./fix_formatting.sh`, which will run the [Black](https://github.com/psf/black) code formatter.

## Features

### Role Distribution

Roles can be distributed arbitrarily and set up with the interactive mapper within the `RoleDistributor.py` file.

To set up a new role distributor, initialize a new session with `!initialize_role_mapping <message_id> [options]`. To get the message ID, hold shift and click on the `ID` icon to the right of the message (make sure you have Developer Mode enabled). Currently, the only option supported is `unique`, which is a flag for this listener that the roles being assigned are unique (ie. only one role from that listener can be assigned to single user at a time).

With the session started, add new mappings with `!add_role_mapping <emote> <role_id>`. Note that you can also mention the role in order to set up the mapping. Both custom and unicode emotes are supported.

Once you're done, finalize the mapping with `!finalize_role_mapping`. This will clear all the reactions on the targeted message, and initialize the mapped reactions.

#### Caveats

- The channel with the role reacts must grant everyone the `Add Reactions` permission. The bot will handle removing reactions that aren't mapped.

- If you delete a mapped message, remember to delete the mapping too (`!delete_role_mapping <message_id>`). There won't be an error, but you won't be able to map those roles again until you've removed the old listeners.

- Roles are unique; you cannot map the same role to multiple listeners or emotes.

- Mapping can only be done by the bot owner at this time (TODO)

### Commands

#### Prerequisite Checking

Commands can be found within the `PrerequisiteChecker.py` file.
ECE/CS course prerequisites can be fetched through using the `!prereq` command with the selected course. For example, using `!prereq cpen333` will list the prerequisites for CPEN333 (System Software Engineering) as CPSC259 or CPEN223. Please ensure there are no spaces when providing the course input. The courses supported can be found in `assets/ece-course-prereqs.csv`.

#### Course Info

Course info can be attained with `!courseinfo <course>`. Note that the course structure should be DEPT### (case-insensitive). The command scrapes the UBC Course Schedule, so the data should be up-to-date. If it fails, use `!prereq <course>` instead. If retrieval fails, the command will attempt to fetch the course from a cached version of the schedule.

#### Repl

Commands can be found within the `Repl.py` file.

This command relies on an external service [[source](https://github.com/lcfyi/repl-api)]. By default, this cog will start uninitialized, and will require the owner of the bot to run `!set_repl <service_url>` to enable the functionality of the cog.

##### Running Locally

If desired, the above repo can be run locally where the bot is hosted. To get started, install `docker` and `docker-compose`. Next, clone the [repo](https://github.com/lcfyi/repl-api) and initialize it by running `docker-compose up`. The first run will take a while depending on your network and host speed, as it has to build the base image that is used to execute the code snippets.

Once the repl service is initialized, this cog can be set up with `!set_repl http://localhost:5000/run`.

#### FAQ

Commands can be found within the `FaqManager.py` file.
A Frequently Asked Questions (FAQ) document can be brought up with the various commands. In addition, it will link to a document which will be hosted on Google Drive and open to suggestions for all ECE members to contribute. The default commands are:

- `!programs`: Brings up program links for ECE, including MASc and MEng.
- `!interviews`: Brings up a self-written ECE interview prep guide, which is a WIP.
- `!leetcode`: Brings up a self-written LeetCode introductory prep guide, which can be found [here](https://docs.google.com/document/d/16BeYJzj_az-8Zv562RgZ0M_mxvCo6W6Thhc0D1oaNwE/edit?usp=sharing).
- `!blind75`: Brings up the Blind 75 LeetCode list, which can be found [here](https://docs.google.com/spreadsheets/d/1O6lu-27mkdEfQAFfMB43vcqZRF57ygtJO2tCDw2ZQaY/edit?usp=sharing).
- `!repo`: Brings up the Github repository for the ECESS Discord Bot.

More default commands can be added by adding them in `assets/default_commands.json`. The structure follows:

```json
"command_name": {
    "description": "description in the help text",
    "content": "content of the command"
}
```

New custom commands can be added with `!add <command> <content>`, which can be brought up by other members with `!<command>`. To remove that custom command, simply invoke `!remove <command>`.

## Troubleshooting

### SSL Certificate Expiration on Windows

The solution can be found on a Github issue comment [here](https://github.com/Rapptz/discord.py/issues/4159#issuecomment-640107584). Downloading and installing the certificate can be done from [here](https://crt.sh/?id=2835394). The download link can be explicitly found [here](https://beans-took-my-kids.reeee.ee/38qB2n.png).

### Member Not Found on Reaction Removal

Please ensure privileged intents are enabled on the server. Otherwise, `guild.get_members` will not return the proper result.

### Unable to Find Message ID

Please verify Developer Mode has been enabled on your server.

### Permission Errors in Console

Generally a 403 error. Ensure the bot privileges are higher than the roles being assigned, which can be adjusted in the server settings.
