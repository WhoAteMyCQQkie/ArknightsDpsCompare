# First of all: Don't Judge me for this code, I know it's neither clean nor efficient, but with the limited amount of thought I put into it, this is the best architecture I could come up with.
# In order for the bot to work you need a "token.txt" file in the same directory as this file, which should contain your discord token (see last 3 lines of this file). Also Change line 48!

#TODO: Easy but tedious tasks that just take a lot of time
# implement the missing operators
# implement more healers (and probably fix the kwargs situation before many more are added)
# implement various total_dmg methods for operators

#TODO: specific Minijobs that really should be done asap
# hoederer/qiubai: low dmg showing their dps with their own application rate of the conditionals, instead of just ignoring it
# Mudrock: include the SP gains from the module for S2 damage calculations
# platinum: fix the dmg bonus, it counts from 0 to 2.5 seconds right now, which should be from 1 to 2.5 seconds i think
# kjera: fix freeze rate, applying cold on a frozen enemy does NOT refresh the duration
# Wisadel: Add S1 and S2, and maybe double check S3's aoe
# kaltsit: the true damage of S3 cant handle changes in max res
# add new modules for ifrit, gladiia.
# muelsyse melee clone. get name is bugged (just compare low mumu to conditionals mumu)

#TODO: bigger changes that may be complicated or even unrealistic
# add average_dmg methods (which include skill down time and ramp up times etc)
# clean up plotting, so that the parts are not scattered around in the code
# efficiency boost: restructure everything so that the atkbuff calculations are done only when instancing the operator, instead of with every call of the skilldps method (may interfere with bbuff)
# add !disclaimer prompt talking about the limits of the bots
# add detail prompt to give an explanation text for complicated graphs (like assumptions for santallas s2 hit-/freezeratio)
# change high/low into high/low/default for unrealistic conditionals (aka chongyue) -> better: add plus ultra prompt to show unrealistically high dmg
# stacks prompt (mlynar, lapluma, gavialter) to increment certain conditionals
# improve enemy prompt: still not good as it is (better formatting, showing enemy hp)
# add kwargs to make the bot understand more text (like "vs heavy" for rosa or "no mines" for ela)
# first collect the operators(aka parse through the entire input) and THEN draw the stuff.
# make it visible in the plot, where which part of the name comes from. (example: typhons text "all crits" gets turned green, green standing for talent2, so people know its lowtalent2 that removes it)

import os
from typing import Callable, List

import discord
import nltk

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
	commands.register('ops', cmds.simple(f"These are the currently available operators: \n{", ".join(operators)[:-1]} \n (Not all operators have all their skills implemented, check the legend of the graph)"))
	commands.register('hops', cmds.simple(f"These are the currently available healers: \n{", ".join(healers)[:-1]}"))
	commands.register('help', cmds.simple("""General use: !dps <opname1> <opname2> ... 
Spaces are used as delimiters, so make sure to keep operator names in one word. This bot can only handle E2 ops with skill lvl 7+ and the result is purely mathematical (no frame counting etc, so the reality typically differs a bit from the result, not that one would notice a < 5% difference ingame):
example: !dps def 0 targets 3 lapluma p4 s2 m1 x2 low ulpianus s2
!guide will show you the available modifiers to the graphs, !ops lists the available operators.
There are also a handful of healers implemented. !hps <opname> ... works similar to !dps. !hops shows the available healers.
Errors do happen, so feel free to double check the results. The Bot will also respond to DMs.
If you want to see how the bot works or expand it, it has a public repository: github.com/WhoAteMyCQQkie/ArknightsDpsCompare
"""))
	commands.register('prompt', cmds.simple("""**Suffixes placed after the operator, affecting only that operator:**
S1,S2,S3, sl7, M0..M3, P1..P6, mod0,modx,mody,modd or just 0,x1,x2,x3,y1,y2,y3,d1,d2,d3
**Prefixes that affect all following operators (not adding a value resets to default values):**
targets <value>, res <value>/def <value>, buff <atk%> <flatAtk> <aspd> <fragile>, level <OpLevel>, hits <receivedHitsPerSecond> (either like 0.33 or 1/3), bbuff <value> (base atk, flat:123, percentage: 25% or 0.25), resshred/defshred (same as bbuff, percent or flat)
**Conditional damage prefixes, affecting all following operators:**
lowtrait/hightrait, lowtalent1/hightalent1, lowtalent2/hightalent2, lowskill/highskill, lowmodule/highmodule
*(just writing low/high sets all 5. you can also use low1,..,low5 or high1,..,high5 for trait,talent1,talent2,skill,module)*
**Prompts for the axis scale, that need to be added before any operators:** maxdef/maxres <value>, split/split2, fix/fixdef/fixres <value> (fix chooses res <100, else def)
**Other prompts:** hide,left,tiny (for the legend),  color (for colorblind people, at the start), text (puts everything after the prompt as title of the graph)
*Most prefix prompts can also be shortened: buff -> b, low/high -> l/h, targets -> t, level -> lv, ...*
"""))
	commands.register('muelsyse', cmds.simple("""There are multiple clones available. The cloned operator will be have the same level,pot and module-lvl as Mumu. Lowtrait removes Mumus bonus trait dmg, lowtalent1 removes the main clone, lowtalent2 removes the stolen atk if the cloned op is melee. lowskill will remove 2 clones from skill 3 or completely remove the extra clones for skill 1/2, otherwise it will assume the main clone is always attacking and calculate the damage with the expected average amount of clones during the skill duration.
As operator input use mumuX or mumuOPERATOR with X:OPERATOR being the following: **1:Dorothy, 2:Ebenholz, 3:Ceobe, 4:Mudrock, 5:Rosa, 6:Skadi, 7:Schwarz**
Adding new ops is not a big deal, so ask WhoAteMyCQQkie if there is one you desperately want."""))
	aliases.register('mumu', 'muelsyse')
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
	content = message.content.lower()[1:].split(' ')

	# Attempt to retrieve the command, and check for aliases
	command_name = content[0]
	alias_result: str = aliases.get(command_name)

	if alias_result is not None:
		command_name = alias_result

	command: Callable[[str], DiscordSendable] = commands.get(command_name)

	if command is not None:
		# Run the command and send the result
		await command(content[1:]).send(message.channel)


if __name__ == "__main__":
	with open("token.txt", encoding="locale") as testfile:
		token = testfile.readline()
	client.run(token)
