# In order for the bot to work you need a "token.txt" file in the same directory as this file, which should contain your discord token. 
# You can add a channel.txt file, too. If the file exists, the bot will only respond to channels listed there. Both channel names and channel ids work. 1 channel per line.

#TODO: Easy but tedious tasks that just take a lot of time
# implement the missing operators
# implement various total_dmg and avg_dmg methods for operators, where that doesnt work automatically
# update the kwargs check for operators (false inputs get passed on as kwarg, operator can check for keywords of their kit)

#TODO: specific Minijobs
# weedy: do some weight calculations for skill 3 and show the true dmg
# add meteorite s2
# hoshiguma: if self.hits > 0, then actually calculate the uptime of the dodge buff from modY
# narantuya: proper frame counting to get the attack intervals more accurate
# nymph: add the avgNecrosis as option
# double check ifrits res shred interactions with her delta module
# dodge mechanic for dagda/flametail s1 and Indra
# ray: s1 killshots refunding ammo improves the actual ooa dps
# kafka: hitdmg numbers in the label
# double check ebenholz dps, it's just weird to calc
# skill 0 for tequila and mlynar average (seeing how the stacks count up)

#TODO: bigger changes that may be complicated or even unrealistic
# s123 prompt to add multiple skills
# !guide image to show things graphically.
# combine prompt to combine 2 ops dps
# clean up plotting, so that the parts are not scattered around in the code
# add detail prompt to give an explanation text for complicated graphs (like assumptions for santallas s2 hit-/freezeratio, or necrosis details)
# add plus ultra prompt to show unrealistically high dmg
# stacks prompt (mlynar, lapluma, gavialter) to increment certain conditionals
# make GIFs for different amounts of targets for example, or different values of fixdef
# drone/summon(count) prompt for summoners
# lower limit for axis scale
# harmacists in healing_formulas, giving them the res prompt as possible outputs
# super massive project: let people upload their krooster data and return an ideal base rotation, based on whether it's 252 or 243, the amount of logins. etc.
# Add GUI

import os
import platform
import sys
import traceback

import discord
from discord.ext import commands
from PIL import Image

import damagecalc.commands as cmds
from damagecalc.damage_formulas import operators
from damagecalc.healing_formulas import healers
from damagecalc.utils import DiscordSendable

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

#Set the accepted channels
if os.path.exists("channels.txt"):
	with open("channels.txt","r") as f:
		channels = f.read().split()
else:
	channels = []

def check_channel(ctx):
	if channels == []: return True
	if isinstance(ctx.channel, discord.TextChannel):
		if str(ctx.channel.id) in channels or ctx.channel.name in channels:
			return True
	elif isinstance(ctx.channel, discord.DMChannel):
		return True ######################################################### this defines if the bot reacts to DMs
	return False


#The main command for the bot. Generates the graphs
@bot.command(aliases=["DPS","Dps"])
@commands.check(check_channel)
async def dps(ctx, *content):
	"""Plots the dps graph"""
	await cmds.dps_command(list(content)).send(ctx.channel)

@bot.command(aliases=["HPS","Hps"])
@commands.check(check_channel)
async def hps(ctx, *content):
	"""Compares hps of operators"""
	await cmds.hps_command(list(content)).send(ctx.channel)

@bot.command(aliases=["Stage"])
@commands.check(check_channel)
async def stage(ctx, *content):
	"""Type !stage for more details"""
	await cmds.stage_command(list(content)).send(ctx.channel)

@bot.command()
@commands.check(check_channel)
async def ops(ctx):
	"""Lists the available operators"""
	output = DiscordSendable(f"These are the currently available operators: \n{', '.join(operators)} \n (Not all operators have all their skills implemented, check the legend of the graph)")
	await output.send(ctx.channel)

@bot.command()
@commands.check(check_channel)
async def hops(ctx):
	"""Lists the available healers"""
	output = DiscordSendable(f"These are the currently available healers: \n{', '.join(healers)}")
	await output.send(ctx.channel)

@bot.command(aliases=["prompt", "prompts"])
@commands.check(check_channel)
async def guide(ctx):
	"""Lists all the prompts with short explanations"""
	output = DiscordSendable("""Any prompt written *before the first* operator will affect all operators, prompts written after an operator will change the settings for that operator alone. global allows you to change the settings affecting all following ops, reset sets everything back to default.
**Prompts without parameters (adding multiple will plot all combinations):**
S1,S2,S3,S0 sl1..sl7,M1..M3, P1..P6, E0,E1,E2 mod0,modx,mody,modd and 1,2,3 for modlvl, or combined: 0,x1,x2,x3,y1,y2,y3,d1,d2,d3
total (total dmg over the skill duration), avg (factoring in skill downtime) (do not work for all operators)
**Prompts, that take parameters:**
targets <value>, trust <value>, level <values>, skilllevel <values>, aspd <value>, fragile <value>, res/def <values>, atk <values> (percentage and/or flat, like 90% or 250), bbuff <values> (base atk, percentage and/or flat), resshred/defshred <values> (percentage and/or flat), sp <value>(for ptilo etc), hits <receivedHitsPerSecond> (either like 0.33 or 1/3),
**Handling conditional damage (turn off talent effects etc.):**
all (plots all possible conditionals), conditional (further shows prompts to get a specific condition), c0...c31 (as given by "conditional", can add multiple)
**or alternatively:** lowtrait/hightrait, lowtalent1/hightalent1, lowtalent2/hightalent2, lowskill/highskill, lowmodule/highmodule, **low/high (sets all previous 5)**
**All following prompts are global and their position does not matter. Prompts for the graph:** 
maxdef/maxres <value>, split/split2 (separates def/res increase), fixdef/fixres <value>, big(increases plotsize), numbers (shows all the dmg numbers)
**Other prompts:** 
hide,left,tiny,short (for the legend), highlight, color (for colorblind people), title (puts everything after the prompt as title of the graph, ignoring further inputs)
""")
	await output.send(ctx.channel)

@bot.command(aliases=["muelsyse"])
@commands.check(check_channel)
async def mumu(ctx):
	"""Guide on how to properly use !dps muelsyse"""
	output = DiscordSendable("""Mumu will use the last operator before her as a clone (including potentials,level,promotion). If no operator is found, Ela will be used instead with the same pot/lvl/promotion as Mumu.
Lowtalent removes the main clone, lowtrait the dmg bonus against blocked. for melee clones, lowtalent2 will remove the steal. for S1/S2 ranged operators some averaged amount of clones will be assumed, which isn't super accurate.
Some ops have innate buffs, that WILL be copied (eunectes s1, eyja with modlvl2+,..). This is not included automatically, but you can add these by adding bbuff XX% to the cloned op.""")
	await output.send(ctx.channel)

@bot.command()
@commands.check(check_channel)
async def ping(ctx):
	await ctx.send("Pong!")

@bot.command()
async def marco(ctx):
	await ctx.send("Polo!")

@bot.command()
async def calc(ctx, *content):
	"""Does math calculations, following python syntax. Accepts x instead of *"""
	if platform.system() == "Linux":
		output = cmds.calc_command_linux(list(content))
	else:
		output = cmds.calc_command(list(content))
	await output.send(ctx.channel)

#Creating the help command
class MyHelpCommand(commands.HelpCommand):
	async def send_bot_help(self, mapping):
		help_message = """General use: !dps <opname1> <opname2> ... 
Spaces are used as delimiters, so make sure to keep operator names in one word. The result is purely mathematical (no frame counting etc, so the reality typically differs a bit from the result, not that one would even notice a < 5% difference):
example: !dps def 0 targets 3 lapluma p4 s2 m1 x2 low ulpianus s2
**The Bot will also respond to DMs.**
!guide will show you the available modifiers to the graphs, !ops lists the available operators.
The same works for healers: !hps <opname> ... works similar to !dps. !hops shows the available healers.
Errors do happen, so feel free to double check the results.
If you want to see how the bot works or expand it, it has a public repository: github.com/WhoAteMyCQQkie/ArknightsDpsCompare
**The commands:**
"""
		for cog, commands_list in mapping.items():
			for command in commands_list:
				if command.name in ["ping", "marco","gui"]: continue
				help_message += f"{command.name}: {command.help}\n"
		await self.context.send(help_message)

	async def send_command_help(self, command):
		await self.context.send(f"**{command.name}**: {command.help}")

bot.help_command = MyHelpCommand()

#Error handling. Usually it will just be a command outside of the valid channels
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure): pass
	else: print(f"An error occurred: {error}")

@bot.event
async def on_command_error(ctx, error):
	# Send or log the full traceback
	tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

	# Optionally send to console or a file
	print(f"Full error:\n{tb}", file=sys.stderr)


if __name__ == "__main__":
	try:
		with open("token.txt", encoding="locale") as f:
			token = f.readline()
		bot.run(token)
	except FileNotFoundError:
		print("""In order to function as a discord bot you need a file "token.txt" containing your discord token in the same directory as disco_bot.py.\nYou can however still use !dps right here in the console, following the normal syntax.""")
		while True:
			print("Please enter your operators and prompts")
			input_text = input()
			result = cmds.dps_command(input_text.split())
			image = Image.open(result.file.fp)
			image.show()
