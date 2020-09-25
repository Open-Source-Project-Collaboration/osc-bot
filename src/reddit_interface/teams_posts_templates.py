# The title templates for reddit posts about teams
# Arg 1: The project name
titles = ["Is anyone interested in collaborating on creating {}?",
          "Would anyone like to work on {}?",
          "Working on {}, anyone interested in collaborating?"]

# The reddit posts body templates
# Arg 1: project description
# Arg 2: repository link
# Arg 3: discord invite link
# Arg 4: team name as in the database
bodies = ["Hello :)\n"
          "I have started collaborating with a group of developers on {}\n\n"

          "If you would like to collaborate with us, here is the Github repository link: {}.\n"
          "If you like the idea and would like to join the project discussion, you can join this discord server: {}, "
          "upvote the rules and type (#!add_me 'your github username' '{}')",

          "Hello,\n"
          "I am currently working with a group of programmers on {}\n\n"

          "If you think this is a good idea, feel free to collaborate with us here: {}\n"
          "You can also join the project discussion on this discord server: {}, just upvote the rules and type "
          '(#!add_me "your github username" "{}")',

          "Hi\n"
          "I have started working with some other programmers on {}\n\n"

          "If you like collaborating with others you can contribute to the repository here: {}.\n"
          "The project discussion is done here: {}. You can join, upvote the rules and type "
          '(#!add_me "your github username" "{}") to be added'
          ]

# Arg 1: Discord username of the poster along with the discord discriminator
# Arg 2: Discord username of the bot along with the discord discriminator
footers = ["This post was made through Discord by {} and automated and submitted to reddit by {}.\n"
           "This is not a self promotional post as the objective behind this post is to help "
           "programmers collaborate with each other"]
