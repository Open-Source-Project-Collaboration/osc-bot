# How it works

In order to create a team, the idea goes through multiple processes as follows:

## The idea voting process
- When a member uses 
[`#!new_idea {language} {idea_name} {idea_explanation}`](06%20-%20Member%20Interface.md#idea-proposing) 
the bot sends a message to [the ideas channel](09%20-%20Channels.md#the-ideas-channel) containing an embed 
(which it will scrape later).
- The title of the embed is the idea name with replacing any whitespaces with a dash and removing any characters that
are not letters.
- The idea explanation field defaults to `N/A`.
- The trials field shows how many times the voting for a certain idea has restarted.
- If the bot reboots during the voting process, it will get the message creation date or the message edit date and the
voting period to this date, then it will subtract the current date from the result to get the required waiting time and
post that in the overview channel. The bot also gets the number of trials done so far from the Embed trials field
**That's why admins should not manually edit (remove embeds) or remove any bot messages in read-only channels.**
- The bot removes any reaction that is not a thumbs up.
- The proposer of an idea can vote on his own idea; however, the vote will not be counted.
- The voting period and the required votes are determined in the [config table](10%20-%20Tables.md#the-config-table).
- An idea is cancelled when the voting restarts three times while the votes are less than the required number. A message
is then sent to the [overview channel](09%20-%20Channels.md#the-ideas-overview-channels) indicating so.
- An idea is approved for the next process 
[(the GitHub usernames gathering process)](#the-github-usernames-gathering-process)
when enough votes are reached and the current trial time ends.

## The GitHub usernames gathering process
- This process is reached after an idea gets enough votes in [the voting process](#the-idea-voting-process).
- A message is sent to the [overview channel](09%20-%20Channels.md#the-ideas-overview-channels) with the participants
names and the idea name in an embed.
- The team role is automatically added to the bot
- A DM is sent to each participant asking for their GitHub account. The message will contain an Embed with the idea name
and the Guild ID.
- The participants which reply receive the team role.
- The time the participants are given to reply is shown in the [config table](10%20-%20Tables.md#the-config-table).
- If a user sends an invalid GitHub username, the bot shall not accept it.
- If a user sends someone else's GitHub username, they can re-enter it and the bot will replace it.
- If a user sends someone else's GitHub username and the 
[(the GitHub usernames gathering process)](#the-github-usernames-gathering-process) ends, they can use
[`#!add_me {github_username} {team_name}`](06%20-%20Member%20Interface.md#team-management) to replace their username.
- If the bot reboots during the process it will resend a message to those who haven't replied and delete the old one
- A required percentage of voters must reply with their GitHub usernames in order for the idea to get accepted, 
this can be found in the [config table](10%20-%20Tables.md#the-config-table).
- The bot indicates if enough voters have replied with their GitHub usernames by checking the participants message in
the [overview channel](09%20-%20Channels.md#the-ideas-overview-channels) and the number of members that have the team
role.
- If the idea gets accepted:
    - The DM message gets deleted and a new one gets sent notifying the voter to check the .
    [overview channel](09%20-%20Channels.md#the-ideas-overview-channels)
    - The message in the [overview channel](09%20-%20Channels.md#the-ideas-overview-channels) gets deleted and a new one
    gets sent indicating that the idea is accepted.
    - The [team creation](#the-team-creation-process) process starts.
- If the idea gets declined:
    - The DM message gets deleted and a new one gets sent notifying the voter to check the 
    [overview channel](09%20-%20Channels.md#the-ideas-overview-channels).
    - The message in the [overview channel](09%20-%20Channels.md#the-ideas-overview-channels) gets deleted and a new one
    gets sent indicating that the idea is declined.
    - The users who haven't replied with their GitHub usernames get warned.

## The team creation process
- This process starts after the [(the GitHub usernames gathering process)](#the-github-usernames-gathering-process) ends
and the idea gets accepted.
- The team role gets removed from the bot.
- A category is created with the team name used in the `new_idea` command after
[the formatting we have mentioned](#the-idea-voting-process) if one doesn't already exist.
- A `general` text channel and a `Collab Room` voice channel are created if the `general` text channel doesn't exist.
- A GitHub team is created if one doesn't exist.
- A GitHub repository is created if one doesn't exist.
- A `leader-voting` channel gets created and the bot mentions each voter in a message.

## After the team creation process
- After the users react to the messages in the `leader-voting` channel. An administrator will do `#!assign_leader` in
the channel and a leader will be chosen.
- Only thumbs up reactions are considered as votes.
- A member can vote for themselves to be a leader and their vote **will be counted**.
- The leader voting process can be started manually by an admin using `#!start_leader_voting {team_name}` if a team leader
isn't present and there isn't a voting process going on.
- Admins will do `#!activity_check` occasionally on Saturdays and the bot will warn the inactive members.


## Side note

Upon addition of any features, please update this list besides creating a new
file to explain both it's logic and implementation details.


> Next, check out [design](02%20-%20Design.md)