# How Does it Work

We have mainly 2 features:

- Ideas
- Actions

Others are not directly usable by anyone (including `Admin`s) and are implicit.
Listed features are explained below:


## Ideas

We keep a list of ideas for our members to agree and work on. Every idea has a
lifespan of 14 days. Upon expiration, if the idea has more than 4 votes it is
considered accepted and CrunchBang automatically generates:

- The GitHub repo for the project.
- A GitHub team assigned to the project, adding voters as members.
- Appropriate Discord channels within a group named after the idea.

> Note: Idea channel **must be read only** and only CrunchBang should be allowed
to edit it. The bot gets confused otherwise.

The channel to use as the `idea list` can be configured with
`#!set_channel idea {channel}` command **but only by Admins**.

**Anyone who isn't an Admin trying that will be kicked due to misuse of priviliges.**

Members can vote for ideas using `:thumbsup:` reaction. The bot automatically
reacts with it to indicate users what they can vote with. CrunchBang warns users
in case of any other reactions. This ensures that we do not belittle or despise
ideas but rather like them only if we do. **Be gentle, be kind...**


## Actions

Actions are predefined functions that can be used only by `Admin`s. They take
input and do something within the server. **They can't touch GitHub.**

Issuing a new action can be done via `#!issue_action` command. Available actions
can be seen using `#!action_list`.

**Again, anyone who isn't an Admin trying that will be kicked due to misuse of priviliges.**


## Side note

Upon addition of any features, please update this list besides creating a new
file to explain both it's logic and implementation details.


> Next, check out [design](02%20-%20Design.md)