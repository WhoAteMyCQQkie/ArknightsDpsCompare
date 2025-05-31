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
# logging of wrong inputs for future improvements

import os
import platform
import sys
import traceback
import asyncio
import json

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
handler_busy = [0,0,0]

CONFIG_TEMPLATE = { #!!!changing this does nothing, change your settings in the config.json file that gets created the first time you run the script
    "token": "YOUR_BOT_TOKEN_HERE",
    "channels": ["general", 1145312466163728425],
	"_comment_channels": "Leave 'channels' empty to respond to every channel",
    "respond_to_dm": True,
    "debug_mode": False,
	"allow_stage_command": True,
	"_comment_include": "stage command needs CN gamedata loaded"
}

try:
	with open("config.json", "r") as f:
		config = json.load(f)
except:
	print("Generating a config file. Please fill in your data.")
	with open("config.json", "w") as f:
		json.dump(CONFIG_TEMPLATE, f, indent=4)
	config = CONFIG_TEMPLATE

channels = config["channels"]
token = config["token"]
respond_to_dm = config["respond_to_dm"]
allow_stage = config["allow_stage_command"]
if allow_stage:
	if not os.path.exists('Database/CN-gamedata/zh_CN/gamedata/excel/stage_table.json'):
		print("In order for the !stage and !animate commands to function you need to download the CN gamefiles. You can do so by running:\ngit submodule update --remote")
		allow_stage = False


#Check for valid channels
def check_channel(ctx):
	if channels == []: return True
	if isinstance(ctx.channel, discord.TextChannel):
		if str(ctx.channel.id) in channels or ctx.channel.name in channels:
			return True
	elif isinstance(ctx.channel, discord.DMChannel):
		return respond_to_dm
	return False


#The main command for the bot. Generates the graphs
@bot.command(aliases=["DPS","Dps"])
@commands.check(check_channel)
async def dps(ctx, *content):
	"""Plots the dps graph"""
	await cmds.dps_command(list(content)).send(ctx.channel)

@bot.command(aliases=["DPH","Dph"])
@commands.check(check_channel)
async def dph(ctx, *content):
	"""Plots the dps graph"""
	await cmds.dps_command(["dph"]+list(content)).send(ctx.channel)

@bot.command(aliases=["HPS","Hps"])
@commands.check(check_channel)
async def hps(ctx, *content):
	"""Compares hps of operators"""
	await cmds.hps_command(list(content)).send(ctx.channel)

@bot.command(aliases=["Stage"])
@commands.check(check_channel)
async def stage(ctx, *content):
	"""Type !stage for more details"""
	if not allow_stage: return
	await cmds.stage_command(list(content)).send(ctx.channel)

@bot.command(aliases=["Animate"])
@commands.check(check_channel)
async def animate(ctx, *content):
	"""Will create a video of the stage, showing spawn points, spawn times, paths and idle durations of all the enemies."""
	if not allow_stage: return
	if os.path.isfile(f'media/videos/StageAnimator/outputs/{list(content)[0].upper()}.mp4'):
		file = discord.File(fp = f'media/videos/StageAnimator/outputs/{list(content)[0].upper()}.mp4', filename=f'media/videos/StageAnimator/outputs/{list(content)[0].upper()}.mp4')
		await DiscordSendable(file=file).send(ctx.channel)
	else:
		from Database.JsonReader import StageData
		stage_data = StageData()
		if not list(content)[0].upper() in stage_data.stages.keys():
			output = DiscordSendable("No valid stage name detected, try !stage to get valid inputs.")
			await output.send(ctx.channel)
		elif sum(handler_busy) == 3:
			output = DiscordSendable("The bot is currently running at max capacity, please wait for earlier requests to finish.")
			await output.send(ctx.channel)
		elif sum(handler_busy) == 2 and len(stage_data.get_enemy_pathing(list(content)[0].upper())) > 199:
			output = DiscordSendable("The last free processing slot is reserved for non annihilation maps, please wait for a less busy time to request those.")
			await output.send(ctx.channel)
		else:
			handler = handler_busy.index(0)
			handler_busy[handler] = 1
			output = DiscordSendable("Generating the animation will take at least 10 minutes, expect way longer. Annihilation will take 10+ hours.")
			await output.send(ctx.channel)
			task = await asyncio.to_thread(cmds.animate_command,list(content),handler)
			handler_busy[handler] = 0
			if task.content == "error":
				output = DiscordSendable(f"An error occurred while processing {list(content)[0]}")
				await output.send(ctx.channel)
			else:
				await task.send(ctx.channel)

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
dph (crudely looks for edges in the graph), total (total dmg over the skill duration), avg (factoring in skill downtime) (do not work for all operators)
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
		if not check_channel(self.context): return
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
				if command.name in ["ping","marco","gui","dph"]: continue
				help_message += f"{command.name}: {command.help}\n"
		await self.context.send(help_message)

	async def send_command_help(self, command):
		await self.context.send(f"**{command.name}**: {command.help}")

bot.help_command = MyHelpCommand()

#Error handling. Usually it will just be a command outside of the valid channels
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CheckFailure): pass
	else:
		tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__)) 
		print(f"Full error:\n{tb}", file=sys.stderr)


if __name__ == "__main__":
	try:
		bot.run(token)
	except:
		print("""No Valid token detected, please change the config.json file.\nYou can still use the dps command locally without a token right here:""")
		while True:
			print("Please enter your operators and prompts")
			input_text = input()
			result = cmds.dps_command(input_text.split())
			image = Image.open(result.file.fp)
			image.show()
