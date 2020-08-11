# Design

OSC-Bot (hereafter will be referred to as CrunchBang '#!') is a bot we make
at OSC Project to automate our process of managing ideas, votes and teams.

Therefore, CrunchBang needs 3 features:

- An interface, for admins to control it's functionality
- An interface, for our members to vote for and/or propose new ideas.
- An internal logic for handling teams, both in GitHub and Discord server


## Admin interface
- `#!set_idea_list {channel}`
    * This sets the channel to keep the ideas in,
    hereafter will be referred to as `idea list`.
- `#!issue_action **args`
    * This issues a predefined action with given arguments.
- `#!action_list`
    * Prints a list of available actions.


## Member interface
- `#!idea_list`
    * Returns the current channel used as the `idea list`.
    * With a prompt as to how to propose a new idea.
- `#!new_idea {idea here}`
    * This creates a new idea in the `idea list` channel.
    * This idea is watched for 14 days, if enough votes are present
    a GitHub repo, a team, with a discord channel group gets created.
    * The person who proposed the idea becomes the lead, others become team
    members.
- `#!help`
    * Prints the commands of Member interface, with descriptions.


> Next, check out [implementation details](03%20-%20Implementation.md)