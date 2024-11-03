# In order for the bot to work you need a "token.txt" file in the same directory as this file, which should contain your discord token (see last 3 lines of this file). Also Change line 48!

#TODO: Easy but tedious tasks that just take a lot of time
# implement the missing operators / Update the old operators to the super().__init__ design
# implement various total_dmg and avg_dmg methods for operators, where that doesnt work automatically
# update the kwargs check for operators (false inputs get passed on as kwarg, operator can check for keywords of their kit)

#TODO: specific Minijobs
# Mudrock: include the SP gains from the module for S2 damage calculations
# kjera: fix freeze rate, applying cold on a frozen enemy does NOT refresh the duration
# indra: dodge mechanics can make use of the hits prompts
# add new modules for ifrit, gladiia.
# weedy: do some weight calculations for skill 3 and show the true dmg
# add meteorite s2
# hoshiguma: if self.hits > 0, then actually calculate the uptime of the dodge buff from modY
# narantuya: proper frame counting to get the attack intervals more accurate
# nymph: add the avgNecrosis as option
# check logos p5

#TODO: bigger changes that may be complicated or even unrealistic
# add spboost to the label of all the skills (affected)
# clean up plotting, so that the parts are not scattered around in the code
# add !disclaimer prompt talking about the limits of the bots
# add detail prompt to give an explanation text for complicated graphs (like assumptions for santallas s2 hit-/freezeratio, or necrosis details)
# change high/low into high/low/default for unrealistic conditionals (aka chongyue) -> better: add plus ultra prompt to show unrealistically high dmg
# stacks prompt (mlynar, lapluma, gavialter) to increment certain conditionals
# rework enemy prompt: still not good as it is (better formatting, showing enemy hp, automate getting the images)
# make it visible in the plot, where which part of the name comes from. (example: typhons text "all crits" gets turned green, green standing for talent2, so people know its lowtalent2 that removes it)
# make GIFs for different amounts of targets for example, or different values of fixdef
# drone/summon(count) prompt for summoners
# lower limit for axis scale
# harmacists in healing_formulas, giving them the res prompt as possible outputs
# stylized plots. for example christmas themed etc.
# skill down dps
# super massive project: let people upload their krooster data and return an ideal base rotation, based on whether it's 252 or 243, the amount of logins. etc.

import os
from typing import Callable, List
import platform

import discord
from PIL import Image

import damagecalc.commands as cmds
from damagecalc.damage_formulas import operators
from damagecalc.healing_formulas import healers
from damagecalc.utils import Registry, DiscordSendable


##############################################
#Bot Settings for the channels it will respond to
VALID_CHANNELS = ['operation-room','bot-spam']
RESPOND_TO_DM = True

intents = discord.Intents.all()
client = discord.Client(intents=intents)

#this part is only needed because i use the same token on my pc for my testserver, whereas the script usually runs on a raspberry pi
if os.path.exists("testrun.txt"):
	VALID_CHANNELS = ['privatebottest']
	RESPOND_TO_DM = False

commands: Registry[str, Callable[[List[str]], DiscordSendable]] = Registry("commands")
aliases: Registry[str, str] = Registry("aliases")

@client.event
async def on_ready():
	print(f"We have logged in as {client.user}")
	print('Registering commands...')
	commands.register('ping', cmds.simple('Pong!'))
	commands.register('marco', cmds.simple('Polo!'))
	commands.register('ops', cmds.simple(f"These are the currently available operators: \n{', '.join(operators)} \n (Not all operators have all their skills implemented, check the legend of the graph)"))
	commands.register('hops', cmds.simple(f"These are the currently available healers: \n{', '.join(healers)}"))
	commands.register('help', cmds.simple("""General use: !dps <opname1> <opname2> ... 
Spaces are used as delimiters, so make sure to keep operator names in one word. This bot can only handle E2 ops with skill lvl 7+ and the result is purely mathematical (no frame counting etc, so the reality typically differs a bit from the result, not that one would notice a < 5% difference ingame):
example: !dps def 0 targets 3 lapluma p4 s2 m1 x2 low ulpianus s2
!guide will show you the available modifiers to the graphs, !ops lists the available operators.
There are also a handful of healers implemented. !hps <opname> ... works similar to !dps. !hops shows the available healers.
Errors do happen, so feel free to double check the results. The Bot will also respond to DMs.
If you want to see how the bot works or expand it, it has a public repository: github.com/WhoAteMyCQQkie/ArknightsDpsCompare
"""))
	commands.register('guide', cmds.simple("""Any prompt written before the first operator will affect all operators, prompts written after an operator will overwrite the original settings for that operator alone. global allows you to change the settings affecting all following ops, reset sets everything back to default.
**Prompts without parameters (adding multiple will plot all combinations):**
S1,S2,S3, sl1..sl7,M1..M3, P1..P6, E0,E1,E2 mod0,modx,mody,modd and 1 2 3 for modlvl, or combined: 0,x1,x2,x3,y1,y2,y3,d1,d2,d3
**Prompts, that take parameters:**
targets <value>, trust <value>, level <values>, skilllevel <values>, aspd <value>, fragile <value>, res/def <values>, atk <values> (percentage and/or flat, like 90% or 250), bbuff <values> (base atk, percentage and/or flat), resshred/defshred <values> (percentage and/or flat), hits <receivedHitsPerSecond> (either like 0.33 or 1/3),
**Conditional damage prefixes, allowing you to turn off the effects of talents etc.:**
lowtrait/hightrait, lowtalent1/hightalent1, lowtalent2/hightalent2, lowskill/highskill, lowmodule/highmodule, **low/high (sets all previous 5)**, conditional (plots all available variations)
**Prompts for the graph:** 
def/res <values> (shows the damage numbers for those def/res values), maxdef/maxres <value>, split/split2, fixdef/fixres <value>
**Other prompts:** 
hide,left,tiny,short (for the legend),  color (for colorblind people), text (puts everything after the prompt as title of the graph, ignoring further inputs)
"""))
	aliases.register('prompt', 'guide')
	aliases.register('prompts', 'guide')
	commands.register('muelsyse', cmds.simple("""Mumu will use the last operator before her as a clone (including potentials,level,promotion). If no operator is found, Ela will be used instead with the same pot/lvl/promotion as Mumu. ONLY OPERATORS OF THE NEW SYSTEM CAN BE CLONED!(which may be all of them by the end of the year).
Lowtalent removes the main clone, lowtrait the dmg bonus against blocked. for melee clones, lowtalent2 will remove the steal. for S1/S2 ranged operators some averaged amount of clones will be assumed, this number is however not accurate, since i havent figured out how to properly estimate that.
Some ops have innate buffs, that WILL be copied (eunectes s1, eyja with modlvl2+,..). This is not included automatically, but you can add these by adding bbuff XX% to the cloned op."""))
	aliases.register('mumu', 'muelsyse')
	if platform.system() == "Linux":
		commands.register('calc', cmds.calc_command_linux)
	else:
		commands.register('calc', cmds.calc_command)
	commands.register('dps', cmds.dps_command)
	commands.register('hps', cmds.hps_command)
	
	print(f"{len(commands)} command(s) and {len(aliases)} alias(es) registered!")

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if isinstance(message.channel, discord.channel.DMChannel) and RESPOND_TO_DM:
		pass
	elif not message.channel.name in VALID_CHANNELS: return

	# Check for bot command flag
	if not message.content.lower().startswith('!'):
		return
	
	# Tokenize the message, removing the flag
	content = message.content.lower()[1:].split()

	# Attempt to retrieve the command, and check for aliases
	command_name = content[0]
	alias_result: str = aliases.get(command_name)

	if alias_result is not None:
		command_name = alias_result

	command: Callable[[List[str]], DiscordSendable] = commands.get(command_name)

	if command is not None:
		# Run the command and send the result
		await command(content[1:]).send(message.channel)


if __name__ == "__main__":
	try:
		with open("token.txt", encoding="locale") as testfile:
			token = testfile.readline()
		client.run(token)
	except FileNotFoundError:
		print("""In order to function as a discord bot you need a file "token.txt" containing your discord token in the same directory as disco_bot.py.\nYou can however still use !dps right here in the console, following the normal syntax.""")
		while True:
			print("Please enter your operators and prompts")
			input_text = input()
			result = cmds.dps_command(input_text.split())
			image = Image.open(result.file.fp)
			image.show()
