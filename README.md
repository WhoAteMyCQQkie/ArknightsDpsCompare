This repository contains a Discord bot that will create graphs comparing different operators dps depending on enemy defense and resistance.
It is currently active on the discord server of DragonGJY (www.youtube.com/@DragonGJY) in the operation-room channel.
The bot was never really meant to become a professional thing and grew past expectations, resulting in some spaghetti code, that is neither optimized nor well written. Viewers discretion is advised.

1. How to use:
The bot requires a token.txt containing the discord token in the same directory as the discoBot.py file.
Change "valid_channels" (just below the imports in discoBot.py) to the channels the bot will respond in.
Note: The !calc command does not work under Windows.
You can then type !help in those channels to get a quick explanation on how to use the bot there. The tl;dr being: write !dps opname1 opname2 ...

2. How to contribute:
The easiest way to contribute is to add to the damageformulas.py or healingformulas.py. There you can just copy the examples of the other operators and change them to fit the newly added operator.
Then you can scroll all the way down and add them to the dictionary and operator list.
You can then execute the file to check for syntax errors and optionally add the operator to the "test_ops" dictionary to check the graph without having to start the main script.

3. Miscellaneous:
For the scuffed enemy prompt to work you need a directory "arkbotimages" containing the image files for the enemies (example format zwillingstürme: zt_01.png -> zt_17.png).
Here, this is part of the .gitignore, because I just took those images from the wiki and I'm not sure about copyright etc. + it needs a rework anyway.

4. Disclaimer:
The bot just calculates the dps based on the damage per hit and the attack interval. It does not take extra frames for animations into account and for the sp lockout of skills like horn s1 it just assumes a duration of 1.2 seconds. For example Exusiais skill 3 just multiplies the damage by 5, even though each shot takes some time.
Likewise, Gladiias calculations ignore the potentially very long animations, favoring her dps numbers. For the total damage, the dps is multiplied with the skill duration, regardless of whether the duration aligns with the attack interval or not,
so you may get the damage of 17.42 attacks. Lastly, for necrosis delta modules, the average uptime with the current dps is assumed. This may also be unrealistic, since logos may not even trigger the fallout against very high res enemies.
Tl;dr the numbers are not 100% accurate and the user has to do some thinking on their own. The bot is best used to compare operators to themselves (masteries, module levels, etc.).
