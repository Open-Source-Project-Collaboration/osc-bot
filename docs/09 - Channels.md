# The channels that are used by the bot
## The ideas channel:
* **Name in config**: `idea-channel`
* **Description of the channel**: this is a read-only channel to which the ideas proposed by the users are sent. The bot
counts the votes on each idea when the voting period ends through the number of thumbs up reactions on the message.

## The ideas overview channels:
* **Name in config**: `overview-channel`
* **Description of the channel**: this is a read-only channel in which information about suggested ideas are shown; this 
includes: the time remaining till the 
[voting](01%20-%20How%20Does%20it%20Work.md#the-idea-voting-process) or the
[GitHub-usernames-gathering process](01%20-%20How%20Does%20it%20Work.md#the-github-usernames-gathering-process) 
ends, the approval/decline of an idea the end of the voting/GitHub-usernames-gathering process and the errors that might 
happen while processing ideas.

## The bot moderation channel
* **Name in config**: `bot-channel`
* **Description of the channel**: this is a read-only channel in which the bot actions are shown; these include:
user warns/kicks and activity of users.

## The finished projects channel
* **Name in config**: `finished-channel`
* **Description of the channel**: this is a read-only channel to which the names of the finished projects and the 
participants of them are sent after the project leader uses the `#!mark_as_finished` command.
