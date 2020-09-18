# The member interface
## Overview
- The member interface contains commands that can be used by members, functions related to these commands and extra admin
commands that depend on these functions. 
- On using any command on the Discord server, please put each parameter 
containing spaces between quotation marks.

## Getting information
- `#!channels`
    * Lists the [currently used channels by the bot](09%20-%20Channels.md); 
    these include: the overview channel, the ideas channels, the bot moderation channel and the finished projects 
    channel
    
- `#!voting_info`
    * Shows information concerning the voting process; these include: the voting period, the required votes for each
    idea, the time the voters are given to reply to the bot with their GitHub usernames, the required percentage of the
    voters that are supposed to reply with their GitHub usernames
    
- `#!list_members {Optional(team_name)}` 
    * If an argument is not provided, the command shows all the users that are enrolled in teams, their team names and
    their GitHub usernames (for administrators only)
    * If an argument is provided, the command shows the users that are enrolled in a certain team, their team name and 
    their Github usernames
    
- `#!help` 
    * Prints a list of the available commands.

## Team management
- `#!add_me {github_username} {team_name}`
    * Adds the user to a current existing team of his choice; the team name provided as an argument must be the same as
    the team name in the role, category, GitHub team and GitHub repository
    
- `#!remove_me {github_username} {team_name}`
    * Removes the user from a team he is enrolled in; the team name provided as an argument must be the same as
    the team name in the role, category, GitHub team and GitHub repository

## Idea proposing
- `#!new_idea {programming_language} {idea_name} {Optional(idea_explanation)}`
    * Proposes a new idea which the bot would send to the idea channel to be voted upon.
    > Please note that the idea name must be less than 45 characters long and it shouldn't include any non-letter
    characters. The bot filters out such characters; however, try not to include them in the idea name to avoid unclear
    final idea names
