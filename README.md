This repository contains a Discord bot that will create graphs comparing different operators dps depending on enemy defense and resistance.
The bot was never really meant to become a professional thing and grew past expectations, resulting in some spaghetti code, that is neither optimized nor well written. Viewers discretion is advised.

1. How to use
The bot requires a token.txt containing the discord token in the same directory as the discoBot.py file.
Change "valid_channels" (just below the imports in discoBot.py) to the channels the bot will respond in.
You can send type !help in those channels to get a quick explanation on how to use the bot there. The tl;dr being: write !dps <opname1> <opname2> ...

2. How to contribute
The easiest way to contribute is to add to the damageformulas.py or healingformulas.py. There you can just copy the examples of the other operators and change them to fit the newly added operator.
Then you can scroll all the way down and add them to the dictionary and operator list.
You can then execute the file to check for syntax errors and optionally add the operator to the "test_ops" dictionary to see the graph without having to start the main script.

3. Miscellaneous
For the scuffed enemy prompt to work you need a directory "arkbotimages" containing the image files for the enemies (example format zwillingstürme: zt_01.png -> zt_17.png).
Here, this is part of the .gitignore, because I just took those images from the wiki and I'm not sure about copyright etc. + it needs a rework anyway.
