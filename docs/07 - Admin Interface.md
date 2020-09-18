# The admin interface
## Overview
This interface includes most of the admin commands. Some admin commands are present in the member interface as they are
dependent on functions that exist there. All the
[commands that are available to the project leaders](08%20-%20Leader%20Interface.md) and the
[commands that are available to members](06%20-%20Member%20Interface.md) are available to the administrators.

## Changing config
- `#!set_channel {db_name} {channel_mention}`
    * Sets [a bot channel](09%20-%20Channels.md) to a channel on the server by mentioning it using a `#`.
    The db_name must match the channel name in the config table without `-channel`; the available ones are: `idea`,
    `overview`, `finished` and `bot`
    * Example: `#!set_channel idea #my-idea-channel` 

- `#!change_voting_period {days} {hours} {minutes} {seconds}`
    * Changes the voting period the bot waits before it accepts/cancels an idea and moves on the GitHub usernames 
    gathering process

- `#!change_required_votes {new_required_votes}`
    * Changes the number of votes it takes to approve an idea
    
- `#!change_github_sleep_time {days} {hours} {minutes} {seconds}`
    * Changes the GitHub-usernames-gathering process period the bot waits before approving/declining an idea based on
    the number of users that have replied to the bot with their GitHub accounts
    
- `#!change_github_required_percentage {new_percentage}` (OUTDATED, the Github percentage is automatically calculated now)
    * Changes the required percentage of the voters that must reply with their GitHub accounts in order to approve an
    idea

## Cleaning up
- `#!purge {db_name}`
    * Purges a [a bot channel](09%20-%20Channels.md). Similar to `#!set_channel`, the db_name must match the 
    channel name in the config table without `-channel`
    
- `#!clean_up_db`
    * Removes from the database the teams that don't have roles assigned to them in the server
    
## Team management
- `#!assign_leader`
    * Use this to assign the leader after the members have voted for their desired one. This command must be called
    in a leader-voting channel
    * The member with the most votes number becomes the project leader.
    
- `#!create_new_team {team_name}`
    * Creates a new team manually without having to start idea voting. This can be used with teams that have existed
    before the bot was made; just make sure the role name, the category name, the repository name and the GitHub team
    name are the same, and the team category has a channel called `general`
    * The bot automatically checks if there are roles, categories, repos and GitHub teams which have the team_name and
    doesn't create new ones
    
- `#!delete_team {team_name}`
    * Deletes a team. This will delete the roles, the category, the channels and the GitHub team; but doesn't delete the
    repository
    
- `#!start_leader_voting {team_name}`
    * Manually starts the leader voting process for a team in case no leader exists, this can happen when the leader
    leaves the team or when the team is manually created
    
## Members management
- `#!activity_check`
    * Checks each member's activity by checking the last time they have contributed to the team repository.
    * If no commits were ever done to the repo, the activity check isn't done on this repo
    * This command can only be run on Saturdays because it checks the start of the week of each member commit (Sunday)
    and if the difference between the week start and the current date is more than 13 days, the member gets warned
    
- `#!warns {user_mention}`
    * Shows the number of warns of a certain user
    
- `#!unwarn {user_mention}`
    * Removes one warning from a certain user
    
## Getting info
- `#!ahelp`
    * Lists the admin commands